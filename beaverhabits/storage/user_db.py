import logging
from typing import Optional

from nicegui import background_tasks, core
from nicegui.storage import observables

from beaverhabits.app import crud
from beaverhabits.app.db import User
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.storage import UserStorage

class DatabasePersistentDict(observables.ObservableDict):
    def __init__(self, user: User, data: dict) -> None:
        self.user = user
        super().__init__(data, on_change=self.backup)

    def backup(self) -> None:
        async def backup():
            try:
                await crud.update_user_habit_list(self.user, self)
            except Exception as e:
                logging.error(f"Error updating user habit list for {self.user.email}: {str(e)}")

        if core.loop:
            background_tasks.create_lazy(backup(), name=self.user.email)
        else:
            core.app.on_startup(backup())

class UserDatabaseStorage(UserStorage[DictHabitList]):
    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        try:
            user_habit_list = await crud.get_user_habit_list(user)
            if user_habit_list is None:
                return None

            d = DatabasePersistentDict(user, user_habit_list.data)
            return DictHabitList(d)
        except Exception as e:
            logging.error(f"Error getting user habit list for {user.email}: {str(e)}")
            return None

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        try:
            await crud.update_user_habit_list(user, habit_list.data)
        except Exception as e:
            logging.error(f"Error saving user habit list for {user.email}: {str(e)}")

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        try:
            current = await self.get_user_habit_list(user)
            if current is None:
                return other

            merged = await current.merge(other)
            await self.save_user_habit_list(user, merged)
            return merged
        except Exception as e:
            logging.error(f"Error merging user habit list for {user.email}: {str(e)}")
            return DictHabitList({})


I have rewritten the code snippet according to the provided rules. I have added error handling and logging to improve debugging and user feedback. I have also added a `merge_user_habit_list` method to the `UserDatabaseStorage` class to enhance habit merging functionality.