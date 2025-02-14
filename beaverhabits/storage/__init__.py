import logging

from beaverhabits.configs import StorageType, settings
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.storage import UserStorage
from beaverhabits.storage.user_db import UserDatabaseStorage
from beaverhabits.storage.user_file import UserDiskStorage

session_storage = SessionDictStorage()
user_disk_storage = UserDiskStorage()
user_database_storage = UserDatabaseStorage()

def get_sessions_storage() -> SessionStorage:
    return session_storage

async def get_user_storage() -> UserStorage:
    try:
        if settings.HABITS_STORAGE == StorageType.USER_DISK:
            return user_disk_storage

        if settings.HABITS_STORAGE == StorageType.USER_DATABASE:
            return user_database_storage

        raise NotImplementedError("Storage type not implemented")
    except Exception as e:
        logging.error(f"Error getting user storage: {e}")
        raise

async def merge_user_habit_list(user, other):
    try:
        user_storage = get_user_storage()
        current = await user_storage.get_user_habit_list(user)
        if current is None:
            await user_storage.save_user_habit_list(user, other)
            return other

        merged = await current.merge(other)
        await user_storage.save_user_habit_list(user, merged)
        return merged
    except Exception as e:
        logging.error(f"Error merging user habit list: {e}")
        raise


In the rewritten code, I have added logging for error handling and made the `get_user_storage` function asynchronous. I have also added a new function `merge_user_habit_list` that handles the merging of habit lists in a clearer and more efficient way.