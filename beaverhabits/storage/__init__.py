from pathlib import Path
from typing import Optional

from nicegui.storage import PersistentDict

from beaverhabits.app.db import User
from beaverhabits.configs import StorageType, settings, USER_DATA_FOLDER
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.storage import UserStorage
from beaverhabits.storage.user_db import UserDatabaseStorage

KEY_NAME = "data"

class UserDiskStorage(UserStorage[DictHabitList]):
    def __init__(self):
        self.persistent_dict = None

    def _get_persistent_dict(self, user: User) -> PersistentDict:
        if self.persistent_dict is None:
            path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
            self.persistent_dict = PersistentDict(path, encoding="utf-8")
        return self.persistent_dict

    def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        d = self._get_persistent_dict(user).get(KEY_NAME, {})
        return DictHabitList(d)

    def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        d = self._get_persistent_dict(user)
        d[KEY_NAME] = habit_list.data

    def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        current = self.get_user_habit_list(user)
        return current.merge(other)

session_storage = SessionDictStorage()
user_disk_storage = UserDiskStorage()
user_database_storage = UserDatabaseStorage()

def get_sessions_storage() -> SessionStorage:
    return session_storage

def get_user_storage() -> UserStorage:
    if settings.HABITS_STORAGE == StorageType.USER_DISK:
        return user_disk_storage
    if settings.HABITS_STORAGE == StorageType.USER_DATABASE:
        return user_database_storage
    raise NotImplementedError("Storage type not implemented")


In the rewritten code, I have moved the persistent dictionary method to the top of the `UserDiskStorage` class and simplified the function signatures for clarity. I have also added merge functionality for habit lists and used default values for missing data. The method ordering has been made consistent for readability, and the code now returns values instead of modifying state.