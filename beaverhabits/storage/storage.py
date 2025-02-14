import datetime
from typing import List, Optional, Protocol

from beaverhabits.app.db import User
from beaverhabits.app.schemas import UserRead

class CheckedRecord(Protocol):
    @property
    def day(self) -> datetime.date: ...

    @property
    def done(self) -> bool: ...

    @done.setter
    def done(self, value: bool) -> None:
        print(f"Setting done status to {value} for {self.day}")

    def __str__(self):
        return f"{self.day} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__

class Habit[R: CheckedRecord](Protocol):
    @property
    def id(self) -> str | int: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value: str) -> None:
        print(f"Updating habit name to {value} for habit {self.id}")

    @property
    def star(self) -> bool: ...

    @star.setter
    def star(self, value: int) -> None:
        print(f"Updating star status to {value} for habit {self.id}")

    @property
    def records(self) -> List[R]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None:
        print(f"Ticking habit {self.id} for {day} with status {done}")

    def __str__(self):
        return self.name

    __repr__ = __str__

class HabitList[H: Habit](Protocol):

    @property
    def habits(self) -> List[H]: ...

    @property
    def order(self) -> List[str]: ...

    @order.setter
    def order(self, value: List[str]) -> None:
        print(f"Updating habit order to {value}")

    async def add(self, name: str) -> None:
        print(f"Adding new habit: {name}")

    async def remove(self, item: H) -> None:
        print(f"Removing habit: {item.name}")

    async def get_habit_by(self, habit_id: str) -> Optional[H]:
        print(f"Fetching habit by id: {habit_id}")

class SessionStorage[L: HabitList](Protocol):
    def get_user_habit_list(self) -> Optional[L]:
        print("Fetching user habit list from session")

    def save_user_habit_list(self, habit_list: L) -> None:
        print("Saving user habit list to session")

class UserStorage[L: HabitList](Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[L]:
        print(f"Fetching user habit list for user: {user.id}")

    async def save_user_habit_list(self, user: User, habit_list: L) -> None:
        print(f"Saving user habit list for user: {user.id}")

    async def merge_user_habit_list(self, user: User, other: L) -> L:
        print(f"Merging user habit list for user: {user.id}")


In this rewritten code, I have added print statements to log actions for better debugging. This helps the user to understand what actions are being performed. I have also added type hints to maintain a clean and organized UI.