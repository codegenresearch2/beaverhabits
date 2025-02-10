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

    def backup(self) -> None:
        async def _backup():
            try:
                await crud.update_user_habit_list(self.user, self)
                logger.info(f"Backup successful for user: {self.user.email}")
            except Exception as e:
                logger.error(f"Backup failed for user: {self.user.email}. Error: {str(e)}")

        background_tasks.create_lazy(_backup(), name=self.user.email)

class UserDatabaseStorage(UserStorage[DictHabitList]):

    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        user_habit_list = await crud.get_user_habit_list(user)
        if user_habit_list is None:
            return None

        d = DatabasePersistentDict(user, user_habit_list.data)
        return DictHabitList(d)

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        await crud.update_user_habit_list(user, habit_list.data)

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        current = await self.get_user_habit_list(user)
        if current is None:
            return other

        merged = await current.merge(other)
        await self.save_user_habit_list(user, merged)
        return merged