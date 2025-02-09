import datetime
from dataclasses import dataclass, field
from typing import Optional

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

    async def load_day(self) -> datetime.date:
        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)
        return date.date()

    async def load_done(self) -> bool:
        return self.data["done"]

    async def save_done(self, value: bool) -> None:
        self.data["done"] = value


@dataclass
class DictHabit(Habit[DictRecord], DictStorage):
    async def load_id(self) -> str:
        if "id" not in self.data:
            self.data["id"] = generate_short_hash(self.data["name"])
        return self.data["id"]

    async def load_name(self) -> str:
        return self.data["name"]

    async def save_name(self, value: str) -> None:
        self.data["name"] = value

    async def load_star(self) -> bool:
        return self.data.get("star", False)

    async def save_star(self, value: int) -> None:
        self.data["star"] = value

    async def load_records(self) -> list[DictRecord]:
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        records = await self.load_records()
        record = next((r for r in records if r.day == day), None)
        if record:
            record.done = done
        else:
            data = {"day": day.strftime(DAY_MASK), "done": done}
            self.data["records"].append(data)


@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    async def load_habits(self) -> list[DictHabit]:
        habits = [DictHabit(d) for d in self.data["habits"]]
        habits.sort(key=lambda x: x.star, reverse=True)
        return habits

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        habits = await self.load_habits()
        for habit in habits:
            if habit.id == habit_id:
                return habit

    async def add(self, name: str) -> None:
        d = {"name": name, "records": [], "id": generate_short_hash(name)}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        self.data["habits"].remove(item.data)