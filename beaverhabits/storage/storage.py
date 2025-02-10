from typing import List, Optional, Protocol, TypeVar
from enum import Enum
import datetime

from beaverhabits.app.db import User

class CheckedRecord(Protocol):
    @property
    def day(self) -> datetime.date: ...

    @property
    def done(self) -> bool: ...

    @done.setter
    def done(self, value: bool) -> None: ...

    def __str__(self):
        return f"{self.day.strftime('%Y-%m-%d')} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__

class HabitStatus(Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"

R = TypeVar('R', bound=CheckedRecord)

class Habit(Protocol[R]):
    @property
    def id(self) -> str | int: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value: str) -> None: ...

    @property
    def star(self) -> bool: ...

    @star.setter
    def star(self, value: int) -> None: ...

    @property
    def status(self) -> HabitStatus: ...

    @status.setter
    def status(self, value: HabitStatus) -> None: ...

    @property
    def records(self) -> List[R]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    def __str__(self):
        return self.name

    __repr__ = __str__

H = TypeVar('H', bound=Habit)

class HabitList(Protocol[H]):

    @property
    def habits(self) -> List[H]: ...

    @property
    def order(self) -> List[str]: ...

    @order.setter
    def order(self, value: List[str]) -> None: ...

    async def add(self, name: str) -> None: ...

    async def remove(self, item: H) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[H]: ...

L = TypeVar('L', bound=HabitList)

class SessionStorage(Protocol[L]):
    def get_user_habit_list(self) -> Optional[L]: ...

    def save_user_habit_list(self, habit_list: L) -> None: ...

class UserStorage(Protocol[L]):
    async def get_user_habit_list(self, user: User) -> Optional[L]: ...

    async def save_user_habit_list(self, user: User, habit_list: L) -> None: ...

    async def merge_user_habit_list(self, user: User, other: L) -> L: ...

I have addressed the feedback provided by the oracle. Here's the updated code snippet:

1. I have defined a type variable `R` bound to `CheckedRecord` and used it in the `Habit` protocol to make it generic.
2. I have added a `records` property and a `ticked_days` property to the `Habit` protocol, as suggested by the gold code.
3. I have added `add` and `remove` methods to the `HabitList` protocol, as suggested by the gold code.
4. I have defined type variables `H` and `L` bound to `Habit` and `HabitList`, respectively, and used them in the `HabitList`, `SessionStorage`, and `UserStorage` protocols to make them generic.
5. I have updated the `__str__` method in the `CheckedRecord` class to match the date formatting used in the gold code.

These changes should bring the code closer to the gold standard.