import datetime
import json
import random
import time
from typing import List

from fastapi import HTTPException
from nicegui import ui

from beaverhabits.app.db import User
from beaverhabits.storage import get_user_dict_storage, session_storage
from beaverhabits.storage.dict import DAY_MASK, DictHabitList
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import generate_short_hash

user_storage = get_user_dict_storage()


def dummy_habit_list(days: List[datetime.date]) -> DictHabitList:
    # Generate a random habit list
    pick = lambda: random.randint(0, 3) == 0
    items = [
        {
            'id': generate_short_hash(name),
            'name': name,
            'records': [
                {'day': day.strftime(DAY_MASK), 'done': pick()}
                for day in days
            ],
        }
        for name in ('Order pizz', 'Running', 'Table Tennis', 'Clean', 'Call mom')
    ]
    return DictHabitList({'items': items})


# Get the session habit list
def get_session_habit_list() -> HabitList | None:
    return session_storage.get_user_habit_list()


# Get a specific habit from the session habit list
async def get_session_habit(habit_id: str) -> Habit:
    habit_list = get_session_habit_list()
    if habit_list is None:
        raise HTTPException(status_code=404, detail='Habit list not found')

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail='Habit not found')

    return habit


# Get or create the session habit list
def get_or_create_session_habit_list(days: List[datetime.date]) -> HabitList:
    if (habit_list := get_session_habit_list()) is not None:
        return habit_list

    habit_list = dummy_habit_list(days)
    session_storage.save_user_habit_list(habit_list)
    return habit_list


# Get the user's habit list
async def get_user_habit_list(user: User) -> HabitList | None:
    return await user_storage.get_user_habit_list(user)


# Get a specific habit from the user's habit list
async def get_user_habit(user: User, habit_id: str) -> Habit:
    habit_list = await get_user_habit_list(user)
    if habit_list is None:
        raise HTTPException(status_code=404, detail='Habit list not found')

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail='Habit not found')

    return habit


# Get or create the user's habit list
async def get_or_create_user_habit_list(user: User, days: List[datetime.date]) -> HabitList:
    habit_list = await get_user_habit_list(user)
    if habit_list is not None:
        return habit_list

    habit_list = dummy_habit_list(days)
    await user_storage.save_user_habit_list(user, habit_list)
    return habit_list


# Export the user's habit list
async def export_user_habit_list(habit_list: HabitList, user_identify: str) -> None:
    # Export the habit list to a JSON file
    if isinstance(habit_list, DictHabitList):
        data = {
            'user_email': user_identify,
            'exported_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **habit_list.data,
        }
        binary_data = json.dumps(data).encode()
        file_name = f'habits_{int(float(time.time()))}.json'
        ui.download(binary_data, file_name)
    else:
        ui.notification('Export failed, please try again later.')
