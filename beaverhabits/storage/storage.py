import datetime
from typing import List, Optional, Protocol

from beaverhabits.app.db import User


class CheckedRecord(Protocol):
    @property
    def day(self) -> datetime.date:
        pass

    @property
    def done(self) -> bool:
        pass

    @done.setter
    def done(self, value: bool) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.day} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__


class Habit[R: CheckedRecord](Protocol):
    @property
    def id(self) -> str | int:
        pass

    @property
    def name(self) -> str:
        pass

    @name.setter
    def name(self, value: str) -> None:
        pass

    @property
    def star(self) -> bool:
        pass

    @star.setter
    def star(self, value: int) -> None:
        pass

    @property
    def records(self) -> List[R]:
        pass

    @property
    def ticked_days(self) -> List[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None:
        pass

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


class HabitList[H: Habit](Protocol):
    @property
    def habits(self) -> List[H]:
        pass

    async def add(self, name: str) -> None:
        pass

    async def remove(self, item: H) -> None:
        pass

    async def get_habit_by(self, habit_id: str) -> Optional[H]:
        pass


class SessionStorage[L: HabitList](Protocol):
    def get_user_habit_list(self) -> Optional[L]:
        pass

    def save_user_habit_list(self, habit_list: L) -> None:
        pass


class UserStorage[L: HabitList](Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[L]:
        pass

    async def save_user_habit_list(self, user: User, habit_list: L) -> None:
        pass

    async def merge_user_habit_list(self, user: User, other: L) -> L:
        pass