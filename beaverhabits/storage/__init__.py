import asyncio
import json
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

    if settings.HABITS_STORAGE == StorageType.USER_DATABASE:
        return user_database_storage

    logging.error("Storage type not implemented")
    raise NotImplementedError("Storage type not implemented")

async def import_habit_list(user, habit_list):
    try:
        user_storage = await get_user_storage()
        current_habit_list = await user_storage.get_user_habit_list(user)

        if current_habit_list is None:
            merged_habit_list = habit_list
        else:
            merged_habit_list = await current_habit_list.merge(habit_list)

        await user_storage.save_user_habit_list(user, merged_habit_list)
        logging.info(f"Successfully imported habit list for user {user.email}")
    except Exception as e:
        logging.error(f"Failed to import habit list for user {user.email}: {str(e)}")


In the rewritten code, I have made the following changes:

1. Made `get_user_storage` an asynchronous function to handle JSON imports asynchronously.
2. Added logging statements to log important actions and exceptions.
3. Created a new function `import_habit_list` that merges the current habit list with the imported habit list intelligently. It logs success or failure messages accordingly.