import logging
from typing import Optional

from nicegui import background_tasks, core
from nicegui.storage import observables

from beaverhabits.app import crud
from beaverhabits.app.db import User
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.storage import UserStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabasePersistentDict(observables.ObservableDict):

    def __init__(self, user: User, data: dict) -> None:
        self.user = user
        super().__init__(data, on_change=self.backup)

    def backup(self) -> None:
        async def backup():
            try:
                await crud.update_user_habit_list(self.user, self)
                logger.info(f"User habit list for {self.user.email} backed up successfully.")
            except Exception as e:
                logger.error(f"Failed to backup user habit list for {self.user.email}: {e}")

        if core.loop:
            background_tasks.create_lazy(backup(), name=self.user.email)
        else:
            core.app.on_startup(backup())


class UserDatabaseStorage(UserStorage[DictHabitList]):
    async def get_user_habit_list(self, user: User) -> Optional[DictHabitList]:
        user_habit_list = await crud.get_user_habit_list(user)
        if user_habit_list is None:
            return None

        d = DatabasePersistentDict(user, user_habit_list.data)
        return DictHabitList(d)

    async def save_user_habit_list(self, user: User, habit_list: DictHabitList) -> None:
        try:
            await crud.update_user_habit_list(user, habit_list.data)
            logger.info(f"User habit list for {user.email} saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save user habit list for {user.email}: {e}")

    async def merge_user_habit_list(self, user: User, other: DictHabitList) -> DictHabitList:
        current = await self.get_user_habit_list(user)
        if current is None:
            return other

        merged_list = await current.merge(other)
        try:
            await crud.update_user_habit_list(user, merged_list.data)
            logger.info(f"User habit list for {user.email} merged successfully.")
        except Exception as e:
            logger.error(f"Failed to merge user habit list for {user.email}: {e}")

        return merged_list