from nicegui import ui

from beaverhabits.frontend.components import (
    HabitAddButton,
    HabitDeleteButton,
    HabitNameInput,
    HabitStarCheckbox,
)
from beaverhabits.frontend.layout import layout
from beaverhabits.storage.storage import HabitList

grid_classes = "w-full gap-0 items-center"

class HabitAddCard(ui.card):
    def __init__(self, habit_list: HabitList, refresh_func):
        super().__init__()
        self.habit_list = habit_list
        self.refresh_func = refresh_func
        self.build()

    def build(self):
        for item in self.habit_list.habits:
            with ui.grid(columns=9, rows=1).classes(grid_classes):
                name = HabitNameInput(item)
                name.classes("col-span-7 break-all")

                star = HabitStarCheckbox(item, self.refresh_func)
                star.props("flat fab-mini color=grey")
                star.classes("col-span-1")

                delete = HabitDeleteButton(item, self.habit_list, self.refresh_func)
                delete.props("flat fab-mini color=grey")
                delete.classes("col-span-1")

        with ui.grid(columns=9, rows=1).classes(grid_classes):
            add = HabitAddButton(self.habit_list, self.refresh_func)
            add.classes("col-span-7")

    def refresh(self):
        # Implement the refresh functionality here
        pass

def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            habit_add_card = HabitAddCard(habit_list, habit_add_card.refresh)
            habit_add_card.refresh_func = habit_add_card.refresh