import asyncio
import logging
from beaverhabits.configs import StorageType, settings
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.storage import UserStorage
from beaverhabits.storage.user_db import UserDatabaseStorage
from beaverhabits.storage.user_file import UserDiskStorage

session_storage = SessionDictStorage()
user_disk_storage = UserDiskStorage()
user_database_storage = UserDatabaseStorage()
sqlite_storage = None


def get_sessions_storage() -> SessionStorage:
    return session_storage


async def get_user_storage() -> UserStorage:
    if settings.HABITS_STORAGE == StorageType.USER_DISK:
        return user_disk_storage
    elif settings.HABITS_STORAGE == StorageType.USER_DATABASE:
        return user_database_storage
    else:
        raise NotImplementedError("Storage type not implemented")


async def import_habit_list(user, habit_list):
    try:
        logging.info("Starting habit list import for user: %s", user.email)
        existing_list = await user_disk_storage.get_user_habit_list(user)
        if existing_list:
            merged_list = await existing_list.merge(habit_list)
            await user_disk_storage.save_user_habit_list(user, merged_list)
            logging.info("Habit list merged successfully for user: %s", user.email)
        else:
            await user_disk_storage.save_user_habit_list(user, habit_list)
            logging.info("Habit list saved successfully for user: %s", user.email)
    except Exception as e:
        logging.error("Failed to import habit list for user: %s, error: %s", user.email, str(e))