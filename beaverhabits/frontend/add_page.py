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

class HabitItem(ui.grid):
    def __init__(self, item, habit_list, refresh_func):
        super().__init__(columns=9, rows=1).classes(grid_classes)
        self.item = item
        self.habit_list = habit_list
        self.refresh_func = refresh_func
        self.build()

    def build(self):
        name = HabitNameInput(self.item)
        name.classes("col-span-7 break-all")

        star = HabitStarCheckbox(self.item, self.refresh_func)
        star.props("flat fab-mini color=grey")
        star.classes("col-span-1")

        delete = HabitDeleteButton(self.item, self.habit_list, self.refresh_func)
        delete.props("flat fab-mini color=grey")
        delete.classes("col-span-1")

@ui.refreshable
class HabitAddCard(ui.card):
    def __init__(self, habit_list):
        super().__init__()
        self.habit_list = habit_list
        self.build()

    def build(self):
        for item in self.habit_list.habits:
            HabitItem(item, self.habit_list, self.refresh)

        with ui.grid(columns=9, rows=1).classes(grid_classes):
            add = HabitAddButton(self.habit_list, self.refresh)
            add.classes("col-span-7")

def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            habit_add_card = HabitAddCard(habit_list)

# Initialize habit_list before calling add_page_ui
habit_list = HabitList()
add_page_ui(habit_list)