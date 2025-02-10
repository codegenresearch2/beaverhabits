import datetime
from typing import List, Optional, Protocol, TypeVar

from beaverhabits.app.db import User
from beaverhabits.storage.dict import DictHabitList

import logging

logger = logging.getLogger(__name__)

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

H = TypeVar('H', bound='Habit')

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
    def records(self) -> List[CheckedRecord]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    async def merge(self, other: H) -> H: ...

    def __str__(self):
        return self.name

    __repr__ = __str__

L = TypeVar('L', bound='HabitList')

class HabitList(Protocol[H]):
    @property
    def habits(self) -> List[H]: ...

    async def add(self, name: str) -> None: ...

    async def remove(self, item: H) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[H]: ...

    async def merge(self, other: L) -> L: ...

class SessionStorage(Protocol[L]):
    def get_user_habit_list(self) -> Optional[L]:
        try:
            # Implementation to get habit list from session
            pass
        except Exception as e:
            logger.error(f"Error getting user habit list from session: {e}")
            return None

    def save_user_habit_list(self, habit_list: L) -> None:
        try:
            # Implementation to save habit list to session
            pass
        except Exception as e:
            logger.error(f"Error saving user habit list to session: {e}")

class UserStorage(Protocol[L]):
    async def get_user_habit_list(self, user: User) -> Optional[L]:
        try:
            # Implementation to get habit list from user storage
            # For example, using DictHabitList from beaverhabits.storage.dict
            return DictHabitList()
        except Exception as e:
            logger.error(f"Error getting user habit list from storage: {e}")
            return None

    async def save_user_habit_list(self, user: User, habit_list: L) -> None:
        try:
            # Implementation to save habit list to user storage
            pass
        except Exception as e:
            logger.error(f"Error saving user habit list to storage: {e}")

    async def merge_user_habit_list(self, user: User, other_user: User) -> None:
        try:
            # Implementation to merge habit lists of two users
            pass
        except Exception as e:
            logger.error(f"Error merging user habit lists: {e}")