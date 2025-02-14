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


async def import_habits_async(user, habits):
    try:
        logging.info(f"Importing habits for user: {user.email}")
        existing_habits = await user_disk_storage.get_user_habit_list(user)
        merged_habits = await existing_habits.merge(habits) if existing_habits else habits
        await user_disk_storage.save_user_habit_list(user, merged_habits)
        logging.info(f"Successfully imported habits for user: {user.email}")
    except Exception as e:
        logging.error(f"Failed to import habits for user: {user.email}, error: {e}")


async def main():
    # Example usage
    user = await User.get_by_email("example@example.com")
    habits = DictHabitList({"habit1": "track1", "habit2": "track2"})
    await import_habits_async(user, habits)


if __name__ == "__main__":
    asyncio.run(main())