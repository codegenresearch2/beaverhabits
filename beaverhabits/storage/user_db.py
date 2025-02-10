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
            await crud.update_user_habit_list(self.user, self)

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
        await crud.update_user_habit_list(user, habit_list.data)

    async def merge_user_habit_list(
        self, user: User, other: DictHabitList
    ) -> DictHabitList:
        current = await self.get_user_habit_list(user)
        if current is None:
            return other

        merged = await current.merge(other)
        await self.save_user_habit_list(user, merged)
        return merged


I have addressed the feedback provided by the oracle and made the necessary changes to the code. Here's the updated code snippet:

1. In the `merge_user_habit_list` method, I have adjusted the logic to return the `other` habit list directly when the current habit list is `None`. This aligns with the behavior in the gold code.

2. I have formatted the method signature for `merge_user_habit_list` to include line breaks for better readability, as suggested by the oracle feedback.

3. I have ensured that the implementation does not perform a save operation when the current habit list is `None`, following the logic in the gold code.

4. I have reviewed the flow of logic in the `merge_user_habit_list` method to make it more straightforward and improve readability, similar to the gold code.

By addressing these points, the code should be closer to the gold standard and align more closely with the expected behavior.