import datetime
from dataclasses import dataclass, field
from typing import Optional

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList, UserStorage
from beaverhabits.utils import generate_short_hash
from beaverhabits.app.db import User

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
        return bool(self.data.get("star", False))

    @star.setter
    def star(self, value: bool) -> None:
        self.data["star"] = value

    @property
    def records(self) -> list[DictRecord]:
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            data = {"day": day.strftime(DAY_MASK), "done": done}
            self.data["records"].append(data)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DictHabit) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def merge(self, other: 'DictHabit') -> 'DictHabit':
        merged_habit = DictHabit()
        merged_habit.data = {**self.data, **other.data}
        merged_habit.id = self.id
        merged_habit.name = self.name
        merged_habit.star = self.star
        merged_habit.data["records"] = list(set(self.data["records"] + other.data["records"]))
        return merged_habit


@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    @property
    def habits(self) -> list[DictHabit]:
        habits = [DictHabit(d) for d in self.data["habits"]]
        habits.sort(key=lambda x: x.star, reverse=True)
        return habits

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        for habit in self.habits:
            if habit.id == habit_id:
                return habit

    async def add(self, name: str) -> None:
        habit = DictHabit()
        habit.name = name
        habit.id = generate_short_hash(name)
        self.data["habits"].append(habit.data)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)

    def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        merged_list = DictHabitList()
        merged_list.data["habits"] = list(set(self.data["habits"] + other.data["habits"]))
        return merged_list


class UserStorageImpl(UserStorage[DictHabitList]):
    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        # Implementation to fetch habit list for a user
        pass

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        # Implementation to save habit list for a user
        pass

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        # Implementation to merge habit lists for a user
        merged_list = DictHabitList()
        merged_list.data["habits"] = list(set(self.data["habits"] + other.data["habits"]))
        return merged_list