import datetime
from dataclasses import dataclass, field
from typing import List, Optional

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
        return datetime.datetime.strptime(self.data["day"], DAY_MASK).date()

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
        record = next((r for r in self.records if r.day == day), None)
        if record is None:
            new_record = DictRecord({"day": day.strftime(DAY_MASK), "done": done})
            self.data["records"].append(new_record)
        else:
            record.done = done

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
        d = {"name": name, "records": [], "id": generate_short_hash(name), "star": False}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)

    def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        merged_list = DictHabitList()
        merged_list.data["habits"] = self.data["habits"] + other.data["habits"]
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
        merged_list.data["habits"] = self.data["habits"] + other.data["habits"]
        return merged_list