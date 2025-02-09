import asyncio
from beaverhabits.configs import StorageType, settings
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.storage import UserStorage
from beaverhabits.storage.user_db import UserDatabaseStorage
from beaverhabits.storage.user_file import UserDiskStorage


async def async_import_json(file_path):
    with open(file_path, 'r') as file:
        data = await file.read()
        return json.loads(data)


class LoggingUserStorage(UserStorage):
    def __init__(self, storage: UserStorage):
        self.storage = storage

    async def get_user_habit_list(self, user):
        try:
            print('Fetching user habit list.')
            return await self.storage.get_user_habit_list(user)
        except Exception as e:
            print(f'Error fetching user habit list: {e}')
            return None

    async def save_user_habit_list(self, user, habit_list):
        try:
            print('Saving user habit list.')
            await self.storage.save_user_habit_list(user, habit_list)
        except Exception as e:
            print(f'Error saving user habit list: {e}')

    async def merge_user_habit_list(self, user, other):
        try:
            print('Merging user habit lists.')
            return await self.storage.merge_user_habit_list(user, other)
        except Exception as e:
            print(f'Error merging user habit lists: {e}')
            return other


session_storage = SessionDictStorage()
user_disk_storage = LoggingUserStorage(UserDiskStorage())
user_database_storage = LoggingUserStorage(UserDatabaseStorage())
sqlite_storage = None


def get_sessions_storage() -> SessionStorage:
    return session_storage


async def get_user_storage() -> UserStorage:
    if settings.HABITS_STORAGE == StorageType.USER_DISK:
        return user_disk_storage

    if settings.HABITS_STORAGE == StorageType.USER_DATABASE:
        return user_database_storage

    raise NotImplementedError('Storage type not implemented')