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
    def _get_persistent_dict(self, user: User) -> PersistentDict:
        path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
        return PersistentDict(path, encoding="utf-8")

    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        persistent_dict = self._get_persistent_dict(user)
        data = persistent_dict.get(KEY_NAME)
        if not data:
            return None
        return DictHabitList(data)

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        persistent_dict = self._get_persistent_dict(user)
        persistent_dict[KEY_NAME] = habit_list.data
        await asyncio.to_thread(persistent_dict.save)

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        current = await self.get_user_habit_list(user)
        if current is None:
            return other
        merged_data = {**current.data, **other.data}
        await self.save_user_habit_list(user, DictHabitList(merged_data))
        return DictHabitList(merged_data)