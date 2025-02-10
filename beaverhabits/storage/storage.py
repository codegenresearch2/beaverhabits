from typing import Generic, List, Protocol, TypeVar
from beaverhabits.app.db import User

class CheckedRecord(Protocol):
    @property
    def day(self) -> datetime.date: ...

    @property
    def done(self) -> bool: ...

    @done.setter
    def done(self, value: bool) -> None: ...

    def __str__(self):
        return f"{self.day} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__

T = TypeVar('T')

class Habit(Generic[T], Protocol):
    @property
    def id(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value: str) -> None: ...

    @property
    def star(self) -> bool: ...

    @star.setter
    def star(self, value: bool) -> None: ...

    @property
    def records(self) -> List[T]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    def __str__(self):
        return self.name

    __repr__ = __str__

class HabitList(Generic[T], Protocol):
    @property
    def habits(self) -> List[T]: ...

    async def add(self, name: str) -> None: ...

    async def remove(self, item: T) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[T]: ...

    async def merge(self, other: "HabitList[T]") -> "HabitList[T]": ...

class SessionStorage(Protocol):
    def get_user_habit_list(self) -> Optional[HabitList[Habit[CheckedRecord]]]: ...

    def save_user_habit_list(self, habit_list: HabitList[Habit[CheckedRecord]]) -> None: ...

class UserStorage(Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[HabitList[Habit[CheckedRecord]]]: ...

    async def save_user_habit_list(self, user: User, habit_list: HabitList[Habit[CheckedRecord]]) -> None: ...

class HabitManager:
    def __init__(self, habit_list: HabitList[Habit[CheckedRecord]]):
        self.habit_list = habit_list

    async def add_habit(self, name: str) -> None:
        await self.habit_list.add(name)

    async def remove_habit(self, habit: Habit[CheckedRecord]) -> None:
        await self.habit_list.remove(habit)

    async def get_habit_by_id(self, habit_id: str) -> Optional[Habit[CheckedRecord]]:
        return await self.habit_list.get_habit_by(habit_id)

    async def merge_habits(self, other_habit_list: HabitList[Habit[CheckedRecord]]) -> None:
        await self.habit_list.merge(other_habit_list)

    async def tick_habit(self, habit: Habit[CheckedRecord], day: datetime.date, done: bool) -> None:
        await habit.tick(day, done)

async def merge_habit_lists(habit_list1: HabitList[Habit[CheckedRecord]], habit_list2: HabitList[Habit[CheckedRecord]]) -> HabitList[Habit[CheckedRecord]]:
    merged_habits = await habit_list1.merge(habit_list2)
    return merged_habits