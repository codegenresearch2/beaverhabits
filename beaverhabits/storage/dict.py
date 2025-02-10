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
    persistent    ->     memory      ->     view
    d0: [x]              d0: [x]
                                            d1: [ ]
    d2: [x]              d2: [x]            d2: [x]
                                            d3: [ ]

    # Update:
    view(update)  ->     memory      ->     persistent
    d1: [ ]
    d2: [ ]              d2: [ ]            d2: [x]
    d3: [x]              d3: [x]            d3: [ ]
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

    def __str__(self):
        return f"{self.day} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__


@dataclass
class DictHabit(Habit[DictRecord]):
    data: dict

    def __init__(self, data: dict):
        self.data = data

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
    def records(self) -> List[DictRecord]:
        return [DictRecord(d) for d in self.data.get("records", [])]

    @property
    def status(self) -> HabitStatus:
        return HabitStatus(self.data.get("status", "normal"))

    @status.setter
    def status(self, value: HabitStatus) -> None:
        self.data["status"] = value.value

    @property
    def ticked_days(self) -> List[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            self.data["records"].append({"day": day.strftime(DAY_MASK), "done": done})

    async def merge(self, other: "DictHabit") -> "DictHabit":
        self_ticks = {r.day for r in self.records if r.done}
        other_ticks = {r.day for r in other.records if r.done}
        result_days = sorted(list(self_ticks | other_ticks))

        merged_data = {
            "name": self.name,
            "records": [{"day": day.strftime(DAY_MASK), "done": True} for day in result_days],
            "status": self.status.value,
        }
        return DictHabit(merged_data)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DictHabit) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.name}<{self.id}>"

    __repr__ = __str__


@dataclass
class DictHabitList(HabitList[DictHabit]):
    data: dict

    def __init__(self, data: dict):
        self.data = data

    @property
    def habits(self) -> List[DictHabit]:
        return [DictHabit(habit) for habit in self.data.get("habits", []) if habit["status"] != "soft_delete"]

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
        habit_data = {
            "name": name,
            "records": [],
            "id": generate_short_hash(name),
            "status": "normal",
        }
        self.data["habits"].append(habit_data)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)

    async def merge(self, other: "DictHabitList") -> "DictHabitList":
        merged_habits = set(self.habits).symmetric_difference(set(other.habits))
        merged_data = {"habits": [habit.data for habit in merged_habits], "order": self.order}
        return DictHabitList(merged_data)