from nicegui import ui
from beaverhabits.frontend.components import (
    HabitAddButton,
    HabitDeleteButton,
    HabitNameInput,
    HabitStarCheckbox,
)
from beaverhabits.frontend.layout import layout
from beaverhabits.storage.storage import Habit, HabitList

grid_classes = "w-full gap-0 items-center"

class HabitItem(ui.grid):
    def __init__(self, habit: Habit, habit_list: HabitList, refresh_func):
        super().__init__(columns=9, rows=1).classes(grid_classes)
        self.habit = habit
        self.habit_list = habit_list
        self.refresh_func = refresh_func
        self.build()

    def build(self):
        name = HabitNameInput(self.habit)
        name.classes("col-span-7 break-all")

        star = HabitStarCheckbox(self.habit, self.refresh_func)
        star.props("flat fab-mini color=grey")
        star.classes("col-span-1")

        delete = HabitDeleteButton(self.habit, self.habit_list, self.refresh_func)
        delete.props("flat fab-mini color=grey")
        delete.classes("col-span-1")

@ui.refreshable
class HabitAddCard(ui.card):
    def __init__(self, habit_list: HabitList):
        super().__init__()
        self.habit_list = habit_list
        self.build()

    def build(self):
        for habit in self.habit_list.habits:
            HabitItem(habit, self.habit_list, self.refresh)

        with ui.grid(columns=9, rows=1).classes(grid_classes):
            add = HabitAddButton(self.habit_list, self.refresh)
            add.classes("col-span-7")

def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            habit_add_card = HabitAddCard(habit_list)

# Initialize habit_list with a concrete class that implements the HabitList protocol
concrete_habit_list = ConcreteHabitList()
add_page_ui(concrete_habit_list)