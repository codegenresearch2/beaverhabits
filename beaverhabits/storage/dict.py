from dataclasses import dataclass, field
import datetime
from typing import List, Optional

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList, HabitStatus
from beaverhabits.utils import generate_short_hash

DAY_MASK = "%Y-%m-%d"
MONTH_MASK = "%Y/%m"

@dataclass(init=False)
class DictStorage:
    data: dict = field(default_factory=dict, metadata={"exclude": True})

@dataclass
class DictRecord(CheckedRecord, DictStorage):
    """
    # Read (d1~d3)
    # persistent    ->     memory      ->     view
    # d0: [x]              d0: [x]
    #                                        d1: [ ]
    # d2: [x]              d2: [x]            d2: [x]
    #                                        d3: [ ]
    #
    # Update:
    # view(update)  ->     memory      ->     persistent
    # d1: [ ]
    # d2: [ ]              d2: [ ]            d2: [x]
    # d3: [x]              d3: [x]            d3: [ ]
    """

    @property
    def day(self) -> datetime.date:
        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)
        return date.date()

    @property
    def done(self) -> bool:
        return self.data["done"]

    @done.setter
    def done(self, value: bool) -> None:
        self.data["done"] = value

@dataclass
class DictHabit(Habit[DictRecord], DictStorage):
    @property
    def id(self) -> str:
        if "id" not in self.data:
            self.data["id"] = generate_short_hash(self.name)
        return self.data["id"]

    @id.setter
    def id(self, value: str) -> None:
        self.data["id"] = value

    @property
    def name(self) -> str:
        return self.data["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.data["name"] = value

    @property
    def star(self) -> bool:
        return self.data.get("star", False)

    @star.setter
    def star(self, value: int) -> None:
        self.data["star"] = value

    @property
    def status(self) -> HabitStatus:
        return HabitStatus(self.data.get("status", HabitStatus.ACTIVE))

    @status.setter
    def status(self, value: HabitStatus) -> None:
        self.data["status"] = value

    @property
    def records(self) -> list[DictRecord]:
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            data = {"day": day.strftime(DAY_MASK), "done": done}
            self.data["records"].append(data)

    async def merge(self, other: "DictHabit") -> "DictHabit":
        self_ticks = {r.day for r in self.records if r.done}
        other_ticks = {r.day for r in other.records if r.done}
        result = sorted(list(self_ticks | other_ticks))

        d = {
            "name": self.name,
            "records": [
                {"day": day.strftime(DAY_MASK), "done": True} for day in result
            ],
        }
        return DictHabit(d)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DictHabit) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.name}<{self.id}>"

    __repr__ = __str__

@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    STATUS_ORDER = {
        HabitStatus.ACTIVE: 0,
        HabitStatus.ARCHIVED: 1,
        HabitStatus.SOLF_DELETED: 2,
    }

    @property
    def habits(self) -> list[DictHabit]:
        habits = [DictHabit(d) for d in self.data["habits"] if DictHabit(d).status != HabitStatus.ARCHIVED]

        # Sort by order and then by status
        habits.sort(key=lambda x: (self.order.index(str(x.id)) if str(x.id) in self.order else float("inf"), self.STATUS_ORDER[x.status]))

        return habits

    @property
    def order(self) -> List[str]:
        return self.data.get("order", [])

    @order.setter
    def order(self, value: List[str]) -> None:
        self.data["order"] = value

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        for habit in self.habits:
            if habit.id == habit_id:
                return habit
        return None

    async def add(self, name: str) -> None:
        if not name:
            raise ValueError("Name cannot be empty")
        d = {"name": name, "records": [], "id": generate_short_hash(name), "status": HabitStatus.ACTIVE}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)

    async def merge(self, other: "DictHabitList") -> "DictHabitList":
        result = set(self.habits).symmetric_difference(set(other.habits))

        # Merge the habit if it exists
        for self_habit in self.habits:
            for other_habit in other.habits:
                if self_habit == other_habit:
                    new_habit = await self_habit.merge(other_habit)
                    result.add(new_habit)

        return DictHabitList({"habits": [h.data for h in result]})

I have addressed the feedback provided by the oracle and made the necessary adjustments to the code. Here are the changes made:

1. **Docstring Formatting**: I have ensured that the formatting of the docstring in `DictRecord` is consistent with the gold code. I have paid attention to the alignment and spacing of comments to match the style exactly.

2. **Status Handling**: In the `DictHabit` class, I have verified that the default value for `HabitStatus` is being retrieved correctly. I have used the appropriate method to access the default status without calling `.value`.

3. **Filtering Habits**: In the `DictHabitList` class, I have refined the logic for filtering habits to ensure that only valid habits are included. I have used a method that explicitly checks the status of each habit as shown in the gold code.

4. **Sorting Logic**: I have reviewed the sorting logic in the `habits` property of `DictHabitList`. I have ensured that habits are sorted first by order and then by status in a way that matches the gold code's approach.

5. **Return Types**: In the `get_habit_by` method, I have ensured that the return type is consistent with the gold code. If a habit is not found, I have explicitly returned `None`.

6. **Use of Optional**: I have checked how I handle cases where a value might not be present. I have ensured that my usage of `Optional` aligns with the conventions in the gold code.

7. **Consistency in Method Definitions**: I have reviewed the method definitions throughout the classes to ensure they are structured and logically consistent with the gold code.

These changes should bring the code closer to the gold standard.