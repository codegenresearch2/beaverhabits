import datetime
from typing import List, Optional, Protocol

from beaverhabits.app.db import User
from beaverhabits.app.schemas import UserRead
from beaverhabits.storage.dict import DictHabitList, DictHabit, DictRecord

class CheckedRecord(Protocol):
    @property
    def day(self) -> datetime.date: ...

    @property
    def done(self) -> bool: ...

    @done.setter
    def done(self, value: bool) -> None:
        self.log_action(f"Set done to {value} for {self.day}")

    def log_action(self, action: str) -> None:
        print(f"[LOG] {action}")

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
        self.log_action(f"Changed name to {value}")

    @property
    def star(self) -> bool: ...

    @star.setter
    def star(self, value: int) -> None:
        self.log_action(f"Set star to {value}")

    @property
    def records(self) -> List[R]: ...

    @property
    def ticked_days(self) -> list[datetime.date]:
        return [r.day for r in self.records if r.done]

    async def tick(self, day: datetime.date, done: bool) -> None:
        self.log_action(f"Ticked {day} with done={done}")

    def log_action(self, action: str) -> None:
        print(f"[LOG] {self.name} - {action}")

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
        self.log_action(f"Changed order to {value}")

    async def add(self, name: str) -> None:
        self.log_action(f"Added habit {name}")

    async def remove(self, item: H) -> None:
        self.log_action(f"Removed habit {item.name}")

    async def get_habit_by(self, habit_id: str) -> Optional[H]: ...

    def log_action(self, action: str) -> None:
        print(f"[LOG] HabitList - {action}")

class SessionStorage[L: HabitList](Protocol):
    def get_user_habit_list(self) -> Optional[L]: ...

    def save_user_habit_list(self, habit_list: L) -> None:
        self.log_action(f"Saved habit list")

    def log_action(self, action: str) -> None:
        print(f"[LOG] SessionStorage - {action}")

class UserStorage[L: HabitList](Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[L]:
        self.log_action(f"Fetched habit list for user {user.id}")
        return DictHabitList({"habits": []})  # Placeholder for actual implementation

    async def save_user_habit_list(self, user: User, habit_list: L) -> None:
        self.log_action(f"Saved habit list for user {user.id}")

    async def merge_user_habit_list(self, user: User, other: L) -> L:
        self.log_action(f"Merged habit list for user {user.id}")
        return DictHabitList({"habits": []})  # Placeholder for actual implementation

    def log_action(self, action: str) -> None:
        print(f"[LOG] UserStorage - {action}")


In the rewritten code, I have added logging functionality to the `CheckedRecord`, `Habit`, `HabitList`, `SessionStorage`, and `UserStorage` classes to meet the user's preference for better debugging. I have also added type hints to the `UserStorage` class methods to improve code clarity and maintainability. The actual implementation of the `UserStorage` class methods is left as a placeholder, as it would require access to a database or other persistent storage.