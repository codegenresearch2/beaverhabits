import datetime
from dataclasses import dataclass, field
from typing import Optional, Set

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList
from beaverhabits.utils import generate_short_hash

DAY_MASK = "%Y-%m-%d"

@dataclass(init=False)
class DictStorage:
    data: dict = field(default_factory=dict, metadata={"exclude": True})

@dataclass
class DictRecord(CheckedRecord, DictStorage):
    """A data class representing a checked record."""

    @property
    def day(self) -> datetime.date:
        """Return the date of the record."""
        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)
        return date.date()

    @property
    def done(self) -> bool:
        """Return whether the record is done."""
        return self.data["done"]

    @done.setter
    def done(self, value: bool) -> None:
        """Set the done status of the record."""
        self.data["done"] = value

@dataclass
class DictHabit(Habit[DictRecord], DictStorage):
    """A data class representing a habit."""

    @property
    def id(self) -> str:
        """Return the ID of the habit."""
        if "id" not in self.data:
            self.data["id"] = generate_short_hash(self.name)
        return self.data["id"]

    @id.setter
    def id(self, value: str) -> None:
        """Set the ID of the habit."""
        self.data["id"] = value

    @property
    def name(self) -> str:
        """Return the name of the habit."""
        return self.data["name"]

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the habit."""
        self.data["name"] = value

    @property
    def star(self) -> bool:
        """Return whether the habit is starred."""
        return self.data.get("star", False)

    @star.setter
    def star(self, value: int) -> None:
        """Set the star status of the habit."""
        self.data["star"] = value

    @property
    def records(self) -> list[DictRecord]:
        """Return the records of the habit."""
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        """Tick the habit for a specific day."""
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            data = {"day": day.strftime(DAY_MASK), "done": done}
            self.data["records"].append(data)

    def merge(self, other: 'DictHabit') -> None:
        """Merge records from another habit into this habit."""
        existing_records = {record.day for record in self.records}
        for record in other.records:
            if record.day not in existing_records:
                self.data["records"].append(record.data)

    def __eq__(self, other: object) -> bool:
        """Check if two habits are equal."""
        if isinstance(other, DictHabit):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Compute the hash of the habit."""
        return hash(self.id)

@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    """A data class representing a list of habits."""

    @property
    def habits(self) -> list[DictHabit]:
        """Return the habits in the list, sorted by star status."""
        habits = [DictHabit(d) for d in self.data["habits"]]
        habits.sort(key=lambda x: x.star, reverse=True)
        return habits

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        """Return the habit with the given ID."""
        for habit in self.habits:
            if habit.id == habit_id:
                return habit

    async def add(self, name: str) -> None:
        """Add a new habit to the list."""
        d = {"name": name, "records": [], "id": generate_short_hash(name)}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        """Remove a habit from the list."""
        self.data["habits"].remove(item.data)

    def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        """Merge habits from another list into this list."""
        merged_habits = set(self.habits)
        merged_habits.update(other.habits)
        merged_data = {"habits": [habit.data for habit in merged_habits]}
        return DictHabitList(merged_data)

I have addressed the feedback from the oracle and made the necessary improvements to the code. Here are the changes made:

1. Added docstrings to classes and methods to enhance documentation.
2. Implemented a `merge` method in the `DictHabit` class to combine records from two habits.
3. Simplified the `__eq__` and `__hash__` methods in the `DictHabit` class.
4. Updated type annotations to match the gold code.
5. Used a set to handle merging habits in the `DictHabitList` class.
6. Ensured that the sorting logic matches the gold code's style and clarity.
7. Structured async methods similarly to the gold code.

The updated code snippet is provided above.