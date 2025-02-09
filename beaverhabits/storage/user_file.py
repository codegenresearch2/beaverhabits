import asyncio
import logging
from pathlib import Path
from typing import Optional

from nicegui.storage import PersistentDict

from beaverhabits.app.db import User
from beaverhabits.configs import USER_DATA_FOLDER
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.storage import UserStorage

KEY_NAME = "data"

class UserDiskStorage(UserStorage[DictHabitList]):
    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        try:
            d = await asyncio.to_thread(self._get_persistent_dict(user).get, KEY_NAME)
            if not d:
                return None
            return DictHabitList(d)
        except Exception as e:
            logging.error(f"Failed to get user habit list for user {user.email}: {e}")
            return None

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        try:
            d = self._get_persistent_dict(user)
            d[KEY_NAME] = habit_list.data
        except Exception as e:
            logging.error(f"Failed to save user habit list for user {user.email}: {e}")

    def _get_persistent_dict(self, user: User) -> PersistentDict:
        path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
        return PersistentDict(path, encoding="utf-8")