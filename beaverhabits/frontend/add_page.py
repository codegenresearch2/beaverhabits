from nicegui import ui

from beaverhabits.frontend.components import (
    HabitAddButton,
    HabitDeleteButton,
    HabitNameInput,
    HabitStarCheckbox,
)
from beaverhabits.frontend.layout import layout
from beaverhabits.storage.storage import HabitList

def validate_habit_name(name):
    if not name:
        raise ValueError("Habit name cannot be empty.")
    if len(name) > 50:
        raise ValueError("Habit name cannot exceed 50 characters.")
    return name

@ui.refreshable
def add_ui(habit_list: HabitList):
    for item in habit_list.habits:
        with ui.grid(columns=9, rows=1).classes("w-full gap-0 items-center"):
            name = HabitNameInput(item)
            name.classes("col-span-7 break-all")
            validate_habit_name(name.value)  # Validate habit name

            star = HabitStarCheckbox(item, add_ui.refresh)
            star.props("flat fab-mini color=grey")
            star.classes("col-span-1")

            delete = HabitDeleteButton(item, habit_list, add_ui.refresh)
            delete.props("flat fab-mini color=grey")
            delete.classes("col-span-1")

def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            add_ui(habit_list)

            with ui.grid(columns=9, rows=1).classes("w-full gap-0 items-center"):
                add = HabitAddButton(habit_list, add_ui.refresh)
                add.classes("col-span-7")