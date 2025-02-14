import datetime
from typing import List, Optional, Protocol

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

class HabitStatus(Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"

class Habit[R: CheckedRecord](Protocol):
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

    async def tick(self, day: datetime.date, done: bool) -> None:
        if record := next((r for r in self.records if r.day == day), None):
            record.done = done
            return f"Item drop event: {record} updated"
        else:
            new_record = R(day=day, done=done)
            self.records.append(new_record)
            return f"Item drop event: {new_record} added"

    def __str__(self):
        return f"{self.name} - {self.status.value}"

    __repr__ = __str__

class HabitList[H: Habit](Protocol):

    @property
    def habits(self) -> List[H]: ...

    @property
    def order(self) -> List[str]: ...

    @order.setter
    def order(self, value: List[str]) -> None: ...

    async def add(self, name: str) -> str:
        new_habit = H(name=name, status=HabitStatus.ACTIVE)
        self.habits.append(new_habit)
        return f"Habit added: {new_habit}"

    async def remove(self, item: H) -> str:
        self.habits.remove(item)
        return f"Habit removed: {item}"

    async def get_habit_by(self, habit_id: str) -> Optional[H]: ...

class SessionStorage[L: HabitList](Protocol):
    def get_user_habit_list(self) -> Optional[L]: ...

    def save_user_habit_list(self, habit_list: L) -> None: ...

class UserStorage[L: HabitList](Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[L]: ...

    async def save_user_habit_list(self, user: User, habit_list: L) -> None: ...

    async def merge_user_habit_list(self, user: User, other: L) -> L:
        current_list = await self.get_user_habit_list(user)
        if current_list:
            merged_list = await current_list.merge(other)
            await self.save_user_habit_list(user, merged_list)
            return merged_list
        else:
            await self.save_user_habit_list(user, other)
            return other