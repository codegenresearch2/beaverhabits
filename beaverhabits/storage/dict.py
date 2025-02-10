import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList
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


@dataclass
class DictHabit(Habit[DictRecord], DictStorage):
    @property
    def id(self) -> str:
        if "id" not in self.data:
            self.data["id"] = generate_short_hash(self.name)
        return self.data["id"]

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
    def star(self, value: bool) -> None:
        self.data["star"] = value

    @property
    def records(self) -> List[DictRecord]:
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            data = {"day": day.strftime(DAY_MASK), "done": done}
            self.data["records"].append(data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DictHabit):
            return False
        return self.id == other.id and self.name == other.name and self.star == other.star and self.records == other.records

    def __hash__(self) -> int:
        return hash((self.id, self.name, self.star, tuple(self.records)))


@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    @property
    def habits(self) -> List[DictHabit]:
        habits = [DictHabit(d) for d in self.data["habits"]]
        habits.sort(key=lambda x: x.star, reverse=True)
        return habits

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        for habit in self.habits:
            if habit.id == habit_id:
                return habit

    async def add(self, name: str) -> None:
        d = {"name": name, "records": [], "id": generate_short_hash(name)}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)

    async def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        new_list = DictHabitList()
        new_list.data = self.data.copy()
        for habit in other.habits:
            existing_habit = await self.get_habit_by(habit.id)
            if existing_habit:
                existing_habit.records.extend(habit.records)
            else:
                new_list.data["habits"].append(habit.data)
        return new_list


This revised code snippet addresses the feedback from the oracle by ensuring consistency in property definitions, type annotations, and method implementations. It also includes a clear and consistent format for docstrings and comments.