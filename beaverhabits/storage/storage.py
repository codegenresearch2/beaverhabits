from typing import Generic, List, Optional, TypeVar, Protocol
import datetime

# Type variables for generics
R = TypeVar('R', bound='CheckedRecord')
H = TypeVar('H', bound='Habit')

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


class Habit(Generic[R], Protocol):
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
    def records(self) -> List[R]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    def __str__(self):
        return self.name

    __repr__ = __str__


class HabitList(Generic[H], Protocol):
    @property
    def habits(self) -> List[H]: ...

    async def add(self, name: str) -> None: ...

    async def remove(self, item: H) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[H]: ...

    async def merge(self, other: "HabitList") -> "HabitList": ...


class SessionStorage(Generic[H], Protocol):
    def get_user_habit_list(self) -> Optional[HabitList[H]]: ...

    def save_user_habit_list(self, habit_list: HabitList[H]) -> None: ...


class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class UserStorage(Generic[H], Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[HabitList[H]]: ...

    async def save_user_habit_list(self, user: User, habit_list: HabitList[H]) -> None: ...

    async def merge_user_habit_list(self, user: User, habit_list: HabitList[H]) -> Optional[HabitList[H]]: ...