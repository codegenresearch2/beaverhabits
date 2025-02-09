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
    Represents a record of a habit check on a specific day.
    """
    @property
    def day(self) -> datetime.date:
        """The date when the habit was checked."""
        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)
        return date.date()

    @property
    def done(self) -> bool:
        """Indicates whether the habit was completed on the given day."""
        return self.data["done"]

    @done.setter
    def done(self, value: bool) -> None:
        """Sets the completion status of the habit for the given day."""
        self.data["done"] = value

@dataclass
class DictHabit(Habit[DictRecord], DictStorage):
    """
    Represents a habit with a name and a list of records.
    """
    @property
    def id(self) -> str:
        """The unique identifier for the habit."""
        if "id" not in self.data:
            self.data["id"] = generate_short_hash(self.name)
        return self.data["id"]

    @id.setter
    def id(self, value: str) -> None:
        """Sets the unique identifier for the habit."""
        self.data["id"] = value

    @property
    def name(self) -> str:
        """The name of the habit."""
        return self.data["name"]

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the habit."""
        self.data["name"] = value

    @property
    def star(self) -> bool:
        """Indicates whether the habit is starred."""
        return self.data.get("star", False)

    @star.setter
    def star(self, value: int) -> None:
        """Sets the starred status of the habit."""
        self.data["star"] = value

    @property
    def records(self) -> list[DictRecord]:
        """The list of records for the habit."""
        return [DictRecord(d) for d in self.data["records"]]

    async def tick(self, day: datetime.date, done: bool) -> None:
        """
        Ticks the habit for a specific day, marking it as done or not done.
        :param day: The date to tick.
        :param done: True if the habit was completed, False otherwise.
        """
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            self.data["records"].append({"day": day.strftime(DAY_MASK), "done": done})

    def __eq__(self, other: object) -> bool:
        """
        Checks if two DictHabit instances are equal.
        :param other: The other DictHabit instance to compare with.
        :return: True if the instances are equal, False otherwise.
        """
        return isinstance(other, DictHabit) and self.id == other.id

    def __hash__(self) -> int:
        """
        Returns the hash of the habit's id.
        :return: The hash value of the habit's id.
        """
        return hash(self.id)

@dataclass
class DictHabitList(HabitList[DictHabit], DictStorage):
    """
    Represents a list of habits.
    """
    @property
    def habits(self) -> list[DictHabit]:
        """The list of habits."""
        habits = [DictHabit(d) for d in self.data["habits"]]
        habits.sort(key=lambda x: x.star, reverse=True)
        return habits

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        """
        Gets a habit by its id.
        :param habit_id: The id of the habit to retrieve.
        :return: The habit with the specified id, or None if not found.
        """
        for habit in self.habits:
            if habit.id == habit_id:
                return habit

    async def add(self, name: str) -> None:
        """
        Adds a new habit to the list.
        :param name: The name of the habit to add.
        """
        d = {"name": name, "records": [], "id": generate_short_hash(name)}
        self.data["habits"].append(d)

    async def remove(self, item: DictHabit) -> None:
        """
        Removes a habit from the list.
        :param item: The habit to remove.
        """
        self.data["habits"].remove(item.data)

    async def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        """
        Merges another habit list with this one.
        :param other: The habit list to merge with.
        :return: A new DictHabitList instance with the merged habits.
        """
        merged_data = {"habits": []}
        merged_habits = DictHabitList(merged_data)
        for habit in self.habits:
            merged_habits.data["habits"].append(habit.data)
        for habit in other.habits:
            if habit not in merged_habits.habits:
                merged_habits.data["habits"].append(habit.data)
        return merged_habits
