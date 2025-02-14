import logging

from beaverhabits.configs import StorageType, settings
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.storage import UserStorage
from beaverhabits.storage.user_db import UserDatabaseStorage
from beaverhabits.storage.user_file import UserDiskStorage

session_storage = SessionDictStorage()
user_disk_storage = UserDiskStorage()
user_database_storage = UserDatabaseStorage()

async def get_sessions_storage() -> SessionStorage:
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
        user_storage = await get_user_storage()
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

In the rewritten code, I have added logging for error handling and improved the habit merging logic. I have also made the functions asynchronous for better performance. The `merge_user_habit_list` function retrieves the current user habit list, merges it with the provided `other` habit list, and saves the merged list. If there is an error during this process, it is logged and re-raised.