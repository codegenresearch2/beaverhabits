import logging
from typing import Optional

from nicegui import background_tasks, core
from nicegui.storage import observables

from beaverhabits.app import crud
from beaverhabits.app.db import User
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.storage import UserStorage

logger = logging.getLogger(__name__)

class DatabasePersistentDict(observables.ObservableDict):

    def __init__(self, user: User, data: dict) -> None:
        self.user = user
        super().__init__(data, on_change=self.backup)

    async def backup(self) -> None:
        try:
            await crud.update_user_habit_list(self.user, self)
            logger.info(f"Backup successful for user: {self.user.email}")
        except Exception as e:
            logger.error(f"Backup failed for user: {self.user.email}. Error: {str(e)}")

class UserDatabaseStorage(UserStorage[DictHabitList]):

    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        try:
            user_habit_list = await crud.get_user_habit_list(user)
            if user_habit_list is None:
                return None

            d = DatabasePersistentDict(user, user_habit_list.data)
            return DictHabitList(d)
        except Exception as e:
            logger.error(f"Failed to get habit list for user: {user.email}. Error: {str(e)}")

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        try:
            await crud.update_user_habit_list(user, habit_list.data)
            logger.info(f"Habit list saved successfully for user: {user.email}")
        except Exception as e:
            logger.error(f"Failed to save habit list for user: {user.email}. Error: {str(e)}")

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        try:
            current = await self.get_user_habit_list(user)
            if current is None:
                logger.info(f"No existing habit list for user: {user.email}. Using new habit list.")
                return other

            merged = await current.merge(other)
            await self.save_user_habit_list(user, merged)
            logger.info(f"Habit lists merged successfully for user: {user.email}")
            return merged
        except Exception as e:
            logger.error(f"Failed to merge habit lists for user: {user.email}. Error: {str(e)}")