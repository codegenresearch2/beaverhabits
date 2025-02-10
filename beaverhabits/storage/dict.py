import datetime
import logging
from dataclasses import dataclass, field
from typing import Optional

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList, User
from beaverhabits.utils import generate_short_hash

DAY_MASK = "%Y-%m-%d"
MONTH_MASK = "%Y/%m"

@dataclass(init=False)
class DictStorage:
    data: dict = field(default_factory=dict, metadata={"exclude": True})

@dataclass
class DictRecord(CheckedRecord, DictStorage):
    @property
    def day(self) -> datetime.date:
        try:
            date = datetime.datetime.strptime(self.data["day"], DAY_MASK)
            return date.date()
        except Exception as e:
            logging.error(f"Error parsing date: {e}")
            raise

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
    def star(self, value: int) -> None:
        self.data["star"] = value

    @property
    def records(self) -> list[DictRecord]:
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        try:
            if record := next((r for r in self.records if r.day == day), None):
                record.done = done
            else:
                data = {"day": day.strftime(DAY_MASK), "done": done}
                self.data["records"].append(data)
        except Exception as e:
            logging.error(f"Error ticking habit: {e}")
            raise

@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    @property
    def habits(self) -> list[DictHabit]:
        try:
            habits = [DictHabit(d) for d in self.data["habits"]]
            habits.sort(key=lambda x: x.star, reverse=True)
            return habits
        except Exception as e:
            logging.error(f"Error getting habits: {e}")
            raise

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        try:
            for habit in self.habits:
                if habit.id == habit_id:
                    return habit
        except Exception as e:
            logging.error(f"Error getting habit by id: {e}")
            raise

    async def add(self, name: str) -> None:
        try:
            d = {"name": name, "records": [], "id": generate_short_hash(name)}
            self.data["habits"].append(d)
        except Exception as e:
            logging.error(f"Error adding habit: {e}")
            raise

    async def remove(self, item: DictHabit) -> None:
        try:
            self.data["habits"].remove(item.data)
        except Exception as e:
            logging.error(f"Error removing habit: {e}")
            raise

    async def merge(self, other: 'DictHabitList') -> None:
        try:
            for habit in other.habits:
                if existing_habit := await self.get_habit_by(habit.id):
                    existing_habit.data['records'].extend(habit.data['records'])
                else:
                    self.data['habits'].append(habit.data)
        except Exception as e:
            logging.error(f"Error merging habit lists: {e}")
            raise


In this rewritten code, I have added error handling and logging to all methods that could potentially raise an exception. I have also added a `merge` method to the `DictHabitList` class to support habit merging as per the user's preference. This method merges the habits from another `DictHabitList` instance into the current one, extending the records of existing habits and adding new habits.