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
logger = logging.getLogger(__name__)

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
        for name in ("Order pizza", "Running", "Table Tennis", "Clean", "Call mom")
    ]
    return DictHabitList({"habits": items})

def get_habit_list(storage) -> HabitList | None:
    try:
        return storage.get_user_habit_list()
    except Exception as e:
        logger.error(f"Error fetching habit list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch habit list")

def save_habit_list(storage, habit_list: HabitList) -> None:
    try:
        storage.save_user_habit_list(habit_list)
    except Exception as e:
        logger.error(f"Error saving habit list: {e}")
        raise HTTPException(status_code=500, detail="Failed to save habit list")

def get_or_create_habit_list(storage, user: User, days: List[datetime.date]) -> HabitList:
    habit_list = get_habit_list(storage)
    if habit_list is not None:
        return habit_list

    habit_list = create_dummy_habit_list(days)
    save_habit_list(storage, habit_list)
    return habit_list

async def get_habit(storage, user: User, habit_id: str) -> Habit:
    habit_list = get_or_create_habit_list(storage, user, [])
    habit = habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit

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
            raise TypeError("Habit list type not supported for export")
    except Exception as e:
        logger.error(f"Error exporting habit list: {e}")
        ui.notification("Export failed, please try again later.")

async def merge_habit_lists(user: User, other: HabitList) -> HabitList:
    try:
        return await user_storage.merge_user_habit_list(user, other)
    except Exception as e:
        logger.error(f"Error merging habit lists: {e}")
        raise HTTPException(status_code=500, detail="Failed to merge habit lists")


I have rewritten the code to enhance the habit merging functionality, improve error handling and logging, and refactor the code for better organization.

The `get_habit_list` and `save_habit_list` functions have been created to handle the fetching and saving of habit lists from storage. These functions now log any errors that occur during these operations.

The `get_or_create_habit_list` function has been modified to use the `get_habit_list` and `save_habit_list` functions, and to create a dummy habit list if one does not exist.

The `get_habit` function has been updated to use the `get_or_create_habit_list` function.

The `export_habit_list` function has been modified to log any errors that occur during the export process, and to raise a `TypeError` if the habit list type is not supported for export.

A new `merge_habit_lists` function has been added to handle the merging of habit lists. This function logs any errors that occur during the merge process.