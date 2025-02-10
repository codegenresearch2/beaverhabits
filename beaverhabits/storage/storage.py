from typing import Protocol, List, Optional, TypeVar, Generic
import datetime

# Define type variables for generics
R = TypeVar('R', bound='CheckedRecord')
H = TypeVar('H', bound='Habit')
S = TypeVar('S', bound='SessionStorage')

class CheckedRecord:
    @property
    def day(self) -> datetime.date:
        return datetime.date.today()  # Assuming today's date for demonstration

    @property
    def done(self) -> bool: ...

    @done.setter
    def done(self, value: bool) -> None: ...

    def __str__(self):
        return f"{self.day} {'[x]' if self.done else '[ ]'}"

    __repr__ = __str__


class Habit(Protocol[R]):
    @property
    def id(self) -> str | int: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, value: str) -> None: ...

    @property
    def star(self) -> int: ...

    @star.setter
    def star(self, value: int) -> None: ...

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

    async def merge(self, other: "HabitList[H]") -> "HabitList[H]": ...


class SessionStorage(Generic[H], Protocol):
    def get_user_habit_list(self) -> Optional[HabitList[H]]: ...

    def save_user_habit_list(self, habit_list: HabitList[H]) -> None: ...


class UserStorage(Protocol):
    async def get_user_habit_list(self, user: User) -> Optional[HabitList]: ...

    async def save_user_habit_list(self, user: User, habit_list: HabitList) -> None: ...

    async def merge_user_habit_list(self, user: User, habit_list: HabitList) -> None: ...


class HabitManager:
    def __init__(self, habit_list: HabitList):
        self.habit_list = habit_list

    async def add_habit(self, name: str) -> None:
        await self.habit_list.add(name)

    async def remove_habit(self, habit: Habit) -> None:
        await self.habit_list.remove(habit)

    async def get_habit_by_id(self, habit_id: str) -> Optional[Habit]:
        return await self.habit_list.get_habit_by(habit_id)

    async def merge_habits(self, other_habit_list: HabitList) -> None:
        await self.habit_list.merge(other_habit_list)

    async def tick_habit(self, habit: Habit, day: datetime.date, done: bool) -> None:
        await habit.tick(day, done)


async def merge_habit_lists(habit_list1: HabitList, habit_list2: HabitList) -> HabitList:
    merged_habits = await habit_list1.merge(habit_list2)
    return merged_habits