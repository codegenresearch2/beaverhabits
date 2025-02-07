import asyncio\\nfrom beaverhabits.configs import StorageType, settings\\nfrom beaverhabits.storage.session_file import SessionDictStorage, SessionStorage\\nfrom beaverhabits.storage.storage import UserStorage\\nfrom beaverhabits.storage.user_db import UserDatabaseStorage\\nfrom beaverhabits.storage.user_file import UserDiskStorage\\n\\nasync def async_json_import(file_path):\\n    with open(file_path, 'r') as file:\\n        data = await file.read()\\n        return json.loads(data)\\n\\nclass LoggingUserStorage(UserStorage):\\n    def __init__(self, storage: UserStorage):\\n        self.storage = storage\\n    async def get_user_habit_list(self, user):\\n        try:\\n            print('Fetching user habit list...')\\n            return await self.storage.get_user_habit_list(user)\\n        except Exception as e:\\n            print(f'Error fetching user habit list: {e}')\\n            return None\\n    async def save_user_habit_list(self, user, habit_list):\\n        try:\\n            print('Saving user habit list...')\\n            await self.storage.save_user_habit_list(user, habit_list)\\n        except Exception as e:\\n            print(f'Error saving user habit list: {e}')\\n    async def merge_user_habit_list(self, user, other):\\n        try:\\n            print('Merging user habit lists...')\\n            return await self.storage.merge_user_habit_list(user, other)\\n        except Exception as e:\\n            print(f'Error merging user habit lists: {e}')\\n\\nsession_storage = SessionDictStorage()\\nuser_disk_storage = LoggingUserStorage(UserDiskStorage())\\nuser_database_storage = LoggingUserStorage(UserDatabaseStorage())\\nsqlite_storage = None\\n\\ndef get_sessions_storage() -> SessionStorage:\\n    return session_storage\\n\\ndef get_user_storage() -> UserStorage:\\n    if settings.HABITS_STORAGE == StorageType.USER_DISK:\\n        return user_disk_storage\\n    elif settings.HABITS_STORAGE == StorageType.USER_DATABASE:\\n        return user_database_storage\\n    raise NotImplementedError('Storage type not implemented')