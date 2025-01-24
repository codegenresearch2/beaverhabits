import datetime
import json
import random

from fastapi import HTTPException, Request
from nicegui import app, ui

from beaverhabits.app.auth import user_create, user_create_token, user_get_by_email
from beaverhabits.app.crud import get_user_count
from beaverhabits.app.db import User
from beaverhabits.configs import settings
from beaverhabits.logging import logger
from beaverhabits.storage import get_user_dict_storage, session_storage
from beaverhabits.storage.dict import DAY_MASK, DictHabitList
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import dummy_days, generate_short_hash

user_storage = get_user_dict_storage()


def dummy_habit_list(days: list[datetime.date]):
    pick = lambda: random.randint(0, 3) == 0
    items = [
        {
            "id": generate_short_hash(name),
            "name": name,
            "records": [
                {"day": day.strftime(DAY_MASK), "done": True} for day in days if pick()
            ],
        }
        for name in ("Order pizz", "Running", "Table Tennis", "Clean", "Call mom")
    ]
    return DictHabitList({"habits": items})


def get_session_habit_list() -> HabitList | None:
    return session_storage.get_user_habit_list()


async def get_session_habit(habit_id: str) -> Habit:
    habit_list = get_session_habit_list()
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit list not found")

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit


def get_or_create_session_habit_list(days: list[datetime.date]) -> HabitList:
    if (habit_list := get_session_habit_list()) is not None:
        return habit_list

    session_storage.save_user_habit_list(dummy_habit_list(days))

    habit_list = get_session_habit_list()
    if habit_list is None:
        raise Exception("Panic! Failed to load habit list")
    return habit_list


async def get_user_habit_list(user: User) -> HabitList:
    habit_list = await user_storage.get_user_habit_list(user)
    if habit_list is None:
        logger.warning(f"Failed to load habit list for user {user.email}")
        raise HTTPException(
            status_code=404,
            detail="The habit list data may be broken or missing, please contact the administrator.",
        )
    return habit_list


async def get_user_habit(user: User, habit_id: str) -> Habit:
    habit_list = await get_user_habit_list(user)

    habit = await habit_list.get_habit_by(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit


async def get_or_create_user_habit_list(
    user: User, days: list[datetime.date]
) -> HabitList:
    try:
        return await get_user_habit_list(user)
    except HTTPException:
        logger.warning(f"Failed to load habit list for user {user.email}")
        pass

    logger.info(f"Creating dummy habit list for user {user.email}")
    await user_storage.save_user_habit_list(user, dummy_habit_list(days))

    habit_list = await get_user_habit_list(user)
    if habit_list is None:
        raise Exception("Panic! Failed to load habit list")
    return habit_list


async def export_user_habit_list(habit_list: HabitList, user_identify: str) -> None:
    # json to binary
    now = datetime.datetime.now()
    if isinstance(habit_list, DictHabitList):
        data = {
            "user_email": user_identify,
            "exported_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            **habit_list.data,
        }
        binary_data = json.dumps(data).encode()
        file_name = f"beaverhabits_{now.strftime('%Y_%m_%d')}.json"
        ui.download(binary_data, file_name)
    else:
        ui.notification("Export failed, please try again later.")


async def validate_max_user_count():
    if await get_user_count() >= settings.MAX_USER_COUNT > 0:
        raise HTTPException(status_code=404, detail="User limit reached")


async def login_user(user: User) -> None:
    token = await user_create_token(user)
    if token is not None:
        app.storage.user.update({"auth_token": token})


async def register_user(email: str, password: str = "") -> User:
    user = await user_create(email=email, password=password)
    # Create a dummy habit list for the new users
    await get_or_create_user_habit_list(user, await dummy_days(31))
    return user


async def authorize_gui(_: Request, user: User | None) -> bool:
    return bool(user and user.is_active)


async def authorize_local_email(_: Request, user: User | None) -> bool:
    if not settings.TRUSTED_LOCAL_EMAIL:
        return False

    # Is user already authorized
    email = settings.TRUSTED_LOCAL_EMAIL
    if user and user.email == email:
        return True

    # Authorize user
    local_user = await user_get_by_email(email)
    if not local_user:
        local_user = await register_user(email)
    await login_user(local_user)
    return True


async def authorize_trusted_email(request: Request, user: User | None) -> bool:
    if not settings.TRUSTED_EMAIL_HEADER:
        return False

    # Is user already authorized
    email = request.headers.get(settings.TRUSTED_EMAIL_HEADER, "")
    if user and user.email == email:
        return True

    # Authorize user
    user = await user_get_by_email(email)
    if user:
        await login_user(user)
        return True

    return False
