import datetime
import json
import random
import time
import logging
from typing import List

from fastapi import HTTPException
from nicegui import ui

from beaverhabits.app.db import User
from beaverhabits.storage import get_user_storage, session_storage
from beaverhabits.storage.dict import DAY_MASK, DictHabitList
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import generate_short_hash

user_storage = get_user_storage()

def create_dummy_habit_list(days: List[datetime.date]):
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

def get_habit_list(storage, user=None):
    try:
        if user:
            return storage.get_user_habit_list(user)
        else:
            return storage.get_user_habit_list()
    except Exception as e:
        logging.error(f"Error getting habit list: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_habit(storage, habit_id: str, user=None):
    habit_list = get_habit_list(storage, user)
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit list not found")

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit

async def get_or_create_habit_list(storage, days: List[datetime.date], user=None):
    habit_list = get_habit_list(storage, user)
    if habit_list is not None:
        return habit_list

    habit_list = create_dummy_habit_list(days)
    if user:
        await storage.save_user_habit_list(user, habit_list)
    else:
        storage.save_user_habit_list(habit_list)
    return habit_list

async def export_habit_list(storage, habit_list: HabitList, user_identify: str) -> None:
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
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def merge_habit_lists(user: User, other: HabitList):
    try:
        user_habit_list = await get_or_create_user_habit_list(user, [])
        merged_habit_list = await user_storage.merge_user_habit_list(user, other)
        return merged_habit_list
    except Exception as e:
        logging.error(f"Error merging habit lists: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


In this rewritten code, I have added error handling and logging as per the user's preference. I have also refactored the code for better organization by creating helper functions for getting and creating habit lists. I have also added a function for merging habit lists as per the user's preference.