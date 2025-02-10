from nicegui import ui

from beaverhabits.frontend.components import (
    HabitAddButton,
    HabitDeleteButton,
    HabitNameInput,
    HabitStarCheckbox,
    HabitAddCard,
)
from beaverhabits.frontend.layout import layout
from beaverhabits.storage.storage import HabitList

grid_classes = "w-full gap-0 items-center"


class AddUI(HabitAddCard):
    def __init__(self, habit_list: HabitList):
        super().__init__(habit_list)
        self.habit_list = habit_list

    def _create_habit_item(self, item):
        with ui.grid(columns=9, rows=1).classes("w-full gap-0 items-center"):
            name = HabitNameInput(item)
            name.classes("col-span-7 break-all")

            star = HabitStarCheckbox(item, self.refresh)
            star.props("flat fab-mini color=grey")
            star.classes("col-span-1")

            delete = HabitDeleteButton(item, self.habit_list, self.refresh)
            delete.props("flat fab-mini color=grey")
            delete.classes("col-span-1")


@ui.refreshable
def add_ui(habit_list: HabitList):
    add_ui_instance = AddUI(habit_list)
    for item in habit_list.habits:
        add_ui_instance._create_habit_item(item)

    with ui.grid(columns=9, rows=1).classes("w-full gap-0 items-center"):
        add = HabitAddButton(habit_list, add_ui.refresh)
        add.classes("col-span-7")


def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            add_ui(habit_list)