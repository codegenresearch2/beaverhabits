import datetime
import json
import random
import time
import logging

from fastapi import HTTPException
from nicegui import ui

from beaverhabits.app.db import User
from beaverhabits.storage import get_user_storage, session_storage
from beaverhabits.storage.dict import DAY_MASK, DictHabitList
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import generate_short_hash

user_storage = get_user_storage()

def create_dummy_habit_list(days: List[datetime.date]) -> HabitList:
    pick = lambda: random.randint(0, 3) == 0
    items = [
        {
            "id": generate_short_hash(name),
            "name": name,
            "records": [
                {"day": day.strftime(DAY_MASK), "done": pick()} for day in days
            ],
        }
        for name in ("Order pizz", "Running", "Table Tennis", "Clean", "Call mom")
    ]
    return DictHabitList({"habits": items})

def get_habit_list(storage: SessionStorage | UserStorage) -> HabitList | None:
    try:
        return storage.get_user_habit_list()
    except Exception as e:
        logging.error(f"Error getting habit list: {e}")
        return None

async def get_habit(user: User, habit_id: str, storage: SessionStorage | UserStorage) -> Habit:
    habit_list = await get_habit_list(storage)
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit list not found")

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit

async def get_or_create_habit_list(user: User, days: List[datetime.date], storage: SessionStorage | UserStorage) -> HabitList:
    habit_list = await get_habit_list(storage)
    if habit_list is not None:
        return habit_list

    habit_list = create_dummy_habit_list(days)
    if storage == user_storage:
        await user_storage.save_user_habit_list(user, habit_list)
    else:
        storage.save_user_habit_list(habit_list)
    return habit_list

async def merge_habit_lists(user: User, other: HabitList) -> HabitList:
    try:
        return await user_storage.merge_user_habit_list(user, other)
    except Exception as e:
        logging.error(f"Error merging habit lists: {e}")
        raise HTTPException(status_code=500, detail="Error merging habit lists")

async def export_habit_list(habit_list: HabitList, user_identify: str) -> None:
    try:
        if isinstance(habit_list, DictHabitList):
            data = {
                "user_email": user_identify,
                "exported_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **habit_list.data,
            }
            binary_data = json.dumps(data).encode()
            file_name = f"habits_{int(float(time.time()))}.json"
            ui.download(binary_data, file_name)
        else:
            ui.notification("Export failed, please try again later.")
    except Exception as e:
        logging.error(f"Error exporting habit list: {e}")
        raise HTTPException(status_code=500, detail="Error exporting habit list")


In this rewritten code, I have added error handling and logging as per the user's preference. I have also refactored the code for better organization. I have created a `get_habit_list` function that takes a `storage` argument, which can be either `session_storage` or `user_storage`. This function is used to get the habit list from the specified storage.

I have also created a `get_or_create_habit_list` function that takes a `storage` argument, which can be either `session_storage` or `user_storage`. This function is used to get the habit list from the specified storage, or create a new one if it doesn't exist.

I have added a `merge_habit_lists` function that merges two habit lists, as per the user's preference. This function uses the `merge_user_habit_list` method of the `user_storage` object.

I have also added a `export_habit_list` function that exports a habit list to a JSON file, as per the user's preference. This function uses the `ui.download` function to download the JSON file.

Finally, I have added logging statements to log errors that occur during the execution of the functions.