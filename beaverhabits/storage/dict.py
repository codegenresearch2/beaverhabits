import datetime
from dataclasses import dataclass, field
from typing import Optional

from beaverhabits.storage.storage import CheckedRecord, Habit, HabitList
from beaverhabits.utils import generate_short_hash

DAY_MASK = "%Y-%m-%d"
MONTH_MASK = "%Y/%m"

@dataclass
class HabitAddCard:
    name: str
    id: str = field(init=False)
    star: bool = False
    records: list[CheckedRecord] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Habit name cannot be empty")
        self.id = generate_short_hash(self.name)

@dataclass
class DictRecord(CheckedRecord):
    day: datetime.date
    done: bool

@dataclass
class DictHabit(Habit[DictRecord]):
    habit_card: HabitAddCard

    @property
    def id(self) -> str:
        return self.habit_card.id

    @property
    def name(self) -> str:
        return self.habit_card.name

    @name.setter
    def name(self, value: str) -> None:
        self.habit_card.name = value

    @property
    def star(self) -> bool:
        return self.habit_card.star

    @star.setter
    def star(self, value: int) -> None:
        self.habit_card.star = value

    @property
    def records(self) -> list[DictRecord]:
        return self.habit_card.records

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
        else:
            self.records.append(DictRecord(day=day, done=done))

@dataclass
class DictHabitList(HabitList[DictHabit]):
    habits: list[DictHabit] = field(default_factory=list)
    order: list[str] = field(default_factory=list)

    async def add(self, name: str) -> None:
        self.habits.append(DictHabit(habit_card=HabitAddCard(name=name)))

    async def remove(self, item: DictHabit) -> None:
        self.habits.remove(item)

    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:
        for habit in self.habits:
            if habit.id == habit_id:
                return habit

    async def merge(self, other: "DictHabitList") -> "DictHabitList":
        result = set(self.habits).symmetric_difference(set(other.habits))

        for self_habit in self.habits:
            for other_habit in other.habits:
                if self_habit == other_habit:
                    new_habit = await self_habit.merge(other_habit)
                    result.add(new_habit)

        return DictHabitList(habits=list(result))