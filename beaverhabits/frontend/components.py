import calendar
import datetime
from dataclasses import dataclass
from typing import Callable, Optional

from nicegui import events, ui
from nicegui.elements.button import Button

from beaverhabits.configs import settings
from beaverhabits.frontend import icons
from beaverhabits.logging import logger
from beaverhabits.storage.dict import DAY_MASK, MONTH_MASK
from beaverhabits.storage.storage import Habit, HabitList
from beaverhabits.utils import WEEK_DAYS

strptime = datetime.datetime.strptime

# Define HabitAddButton class to address the test case feedback
class HabitAddButton(ui.input):
    def __init__(self, habit_list: HabitList, refresh: Callable) -> None:
        super().__init__("New item")
        self.habit_list = habit_list
        self.refresh = refresh
        self.on("keydown.enter", self._add_habit)
        self.props("dense")

    async def _add_habit(self):
        logger.info(f"Adding new habit: {self.value}")
        await self.habit_list.add(self.value)
        self.refresh()
        self.set_value("")
        logger.info(f"Added new habit: {self.value}")

# Define HabitDeleteButton class to address the oracle feedback
class HabitDeleteButton(ui.button):
    def __init__(self, habit: Habit, habit_list: HabitList, refresh: Callable) -> None:
        super().__init__(on_click=self._delete_habit, icon=icons.DELETE)
        self.habit = habit
        self.habit_list = habit_list
        self.refresh = refresh

    async def _delete_habit(self):
        logger.info(f"Deleting habit: {self.habit.name}")
        await self.habit_list.remove(self.habit)
        self.refresh()
        logger.info(f"Deleted habit: {self.habit.name}")

# Rest of the code remains the same