import datetime
import json
import time
from typing import List

from fastapi import HTTPException
from nicegui import ui

from beaverhabits.app.db import User
from beaverhabits.storage import get_user_storage, session_storage
from beaverhabits.storage.dict import DAY_MASK, DictHabitList
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import generate_short_hash

user_storage = get_user_storage()

class DictHabit(DictHabitList.DictHabit):
    def merge(self, other: 'DictHabit') -> 'DictHabit':
        merged_records = {r['day']: r for r in self.records + other.records}
        merged_records.update((r['day'], r) for r in other.records if r['day'] not in merged_records)
        self.records = list(merged_records.values())
        return self

    def __str__(self):
        return f"{self.name} - {'Completed' if self.star else 'Incomplete'} - {len(self.ticked_days)} days completed"

class DictHabitList(DictHabitList):
    def merge(self, other: 'DictHabitList') -> 'DictHabitList':
        merged_habits = {h.id: h for h in self.habits + other.habits}
        merged_habits.update((h.id, h.merge(merged_habits[h.id])) for h in other.habits if h.id in merged_habits)
        self.habits = list(merged_habits.values())
        return self

    def __str__(self):
        return f"Habit List - {len(self.habits)} habits"

def dummy_habit_list(days: List[datetime.date]) -> DictHabitList:
    # ... (rest of the function remains the same)

def get_session_habit_list() -> DictHabitList | None:
    return session_storage.get_user_habit_list()

async def get_session_habit(habit_id: str) -> DictHabit:
    # ... (rest of the function remains the same)

def get_or_create_session_habit_list(days: List[datetime.date]) -> DictHabitList:
    # ... (rest of the function remains the same)

async def get_user_habit_list(user: User) -> DictHabitList | None:
    return await user_storage.get_user_habit_list(user)

async def get_user_habit(user: User, habit_id: str) -> DictHabit:
    # ... (rest of the function remains the same)

async def get_or_create_user_habit_list(user: User, days: List[datetime.date]) -> DictHabitList:
    habit_list = await get_user_habit_list(user)
    if habit_list is not None:
        return habit_list

    habit_list = dummy_habit_list(days)
    await user_storage.save_user_habit_list(user, habit_list)
    return habit_list

async def export_user_habit_list(habit_list: DictHabitList, user_identify: str) -> None:
    # ... (rest of the function remains the same)