import asyncio
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
        path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
        persistent_dict = PersistentDict(path, encoding="utf-8")
        data = persistent_dict.get(KEY_NAME)
        if data is None:
            return None
        return DictHabitList(data)

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
        persistent_dict = PersistentDict(path, encoding="utf-8")
        persistent_dict[KEY_NAME] = habit_list.data

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        current = await self.get_user_habit_list(user)
        if current is None:
            return other
        merged_data = {**current.data, **other.data}
        return DictHabitList(merged_data)