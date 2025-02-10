import datetime
from typing import List, Optional, Protocol
from enum import Enum

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

class Habit(Protocol):
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

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    def __str__(self):
        return self.name

    __repr__ = __str__

class HabitList(Protocol):

    @property
    def habits(self) -> List[Habit]: ...

    @property
    def order(self) -> List[str]: ...

    @order.setter
    def order(self, value: List[str]) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[Habit]: ...

class SessionStorage(Protocol):
    def get_user_habit_list(self) -> Optional[HabitList]: ...

    def save_user_habit_list(self, habit_list: HabitList) -> None: ...

class UserStorage(Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[HabitList]: ...

    async def save_user_habit_list(self, user: User, habit_list: HabitList) -> None: ...

    async def merge_user_habit_list(self, user: User, other: HabitList) -> HabitList:
        current_list = await self.get_user_habit_list(user)
        if current_list is None:
            return other
        merged_list = await current_list.merge(other)
        await self.save_user_habit_list(user, merged_list)
        return merged_list