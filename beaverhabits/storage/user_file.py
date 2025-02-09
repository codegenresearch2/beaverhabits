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
        """
        Returns a PersistentDict instance for the given user.
        """
        path = Path(f"{USER_DATA_FOLDER}/{str(user.email)}.json")
        return PersistentDict(path, encoding="utf-8")

    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        """
        Retrieves the habit list for the given user from disk storage.
        """
        d = self._get_persistent_dict(user).get(KEY_NAME)
        if not d:
            return None
        return DictHabitList(d)

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        """
        Saves the habit list for the given user to disk storage.
        """
        d = self._get_persistent_dict(user)
        d[KEY_NAME] = habit_list.data

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        """
        Merges the habit list of another user with the current user's habit list.
        """
        current = await self.get_user_habit_list(user)
        if current is None:
            return other

        merged_list = await current.merge(other)
        await self.save_user_habit_list(user, merged_list)
        return merged_list