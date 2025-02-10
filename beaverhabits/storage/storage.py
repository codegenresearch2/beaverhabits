import datetime
from typing import List, Optional, Protocol

from beaverhabits.app.db import User
from beaverhabits.app.schemas import HabitCreate, HabitRead, CheckedRecord

class HabitStorage(Protocol):
    @property
    def id(self) -> str | int: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value: str) -> None: ...

    @property
    def card(self) -> bool: ...

    @card.setter
    def card(self, value: bool) -> None: ...

    @property
    def records(self) -> List[CheckedRecord]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None: ...

    async def drag_and_drop(self, new_order: List[str]) -> None: ...

    def __str__(self):
        return self.name

    __repr__ = __str__

class HabitListStorage(Protocol):
    @property
    def habits(self) -> List[HabitStorage]: ...

    async def add(self, habit: HabitCreate) -> None: ...

    async def remove(self, habit_id: str) -> None: ...

    async def get_habit_by(self, habit_id: str) -> Optional[HabitStorage]: ...

    async def drag_and_drop(self, new_order: List[str]) -> None: ...

class SessionStorage(Protocol):
    def get_user_habit_list(self) -> Optional[HabitListStorage]: ...

    def save_user_habit_list(self, habit_list: HabitListStorage) -> None: ...

class UserStorage(Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[HabitListStorage]: ...

    async def save_user_habit_list(self, user: User, habit_list: HabitListStorage) -> None: ...

    async def merge_user_habit_list(self, user: User, other: HabitListStorage) -> HabitListStorage: ...


In the rewritten code, I have made the following changes:

1. Renamed `Habit` to `HabitStorage` and `HabitList` to `HabitListStorage` for better readability and to avoid confusion with the existing `Habit` and `HabitList` classes in `schemas.py`.
2. Added a `card` property to the `HabitStorage` protocol to implement the user's preference for using a card for habit input.
3. Added a `drag_and_drop` method to both `HabitStorage` and `HabitListStorage` protocols to implement the user's preference for drag-and-drop functionality.
4. Updated the function signatures to use the `HabitCreate` and `HabitRead` schemas from `schemas.py` for better consistency and clarity.
5. Updated the `SessionStorage` and `UserStorage` protocols to use `HabitListStorage` instead of `HabitList` for better consistency and clarity.