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

def dummy_habit_list(days: List[datetime.date]):
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

async def get_session_habit_list() -> HabitList | None:
    try:
        return await session_storage.get_user_habit_list()
    except Exception as e:
        logger.error(f"Error getting session habit list: {str(e)}")
        return None

async def get_session_habit(habit_id: str) -> Habit:
    habit_list = await get_session_habit_list()
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit list not found")

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit

async def get_or_create_session_habit_list(days: List[datetime.date]) -> HabitList:
    habit_list = await get_session_habit_list()
    if habit_list is not None:
        return habit_list

    habit_list = dummy_habit_list(days)
    session_storage.save_user_habit_list(habit_list)
    return habit_list

async def get_user_habit_list(user: User) -> HabitList | None:
    try:
        return await user_storage.get_user_habit_list(user)
    except Exception as e:
        logger.error(f"Error getting user habit list: {str(e)}")
        return None

async def get_user_habit(user: User, habit_id: str) -> Habit:
    habit_list = await get_user_habit_list(user)
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit list not found")

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit

async def get_or_create_user_habit_list(user: User, days: List[datetime.date]) -> HabitList:
    habit_list = await get_user_habit_list(user)
    if habit_list is not None:
        return habit_list

    habit_list = dummy_habit_list(days)
    try:
        await user_storage.save_user_habit_list(user, habit_list)
    except Exception as e:
        logger.error(f"Error saving user habit list: {str(e)}")
    return habit_list

async def export_user_habit_list(habit_list: HabitList, user_identify: str) -> None:
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
        logger.error("Export failed, habit list is not of type DictHabitList.")
        ui.notification("Export failed, please try again later.")

In this rewrite, I've made the following changes:\n\n1. Added logging to the `get_session_habit_list`, `get_user_habit_list`, and `get_or_create_user_habit_list` functions to log errors that might occur during execution.\n2. Made the `get_session_habit_list` and `get_user_habit_list` functions asynchronous to follow the user's preference for asynchronous functions.
3. Added error handling to the `get_or_create_user_habit_list` function to log errors that might occur when saving the habit list.
4. Updated the `export_user_habit_list` function to log an error message if the habit list is not of type `DictHabitList`.
5. Left the rest of the code unchanged as it was already following the rules provided.