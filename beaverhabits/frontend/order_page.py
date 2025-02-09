from nicegui import ui

from beaverhabits.frontend import components
from beaverhabits.frontend.components import (HabitAddButton, HabitDeleteButton, HabitNameInput, HabitStarCheckbox)
from beaverhabits.frontend.layout import layout
from beaverhabits.logging import logger
from beaverhabits.storage.storage import HabitList


class Habit:
    def __init__(self, name, status=None):
        self.name = name
        self.status = status if status is not None else 'active'


class DictHabit(Habit):
    def __init__(self, name, status=None):
        super().__init__(name, status)


class HabitList:
    def __init__(self):
        self.habits = []
        self.order = []


class DictHabitList(HabitList):
    def __init__(self):
        super().__init__()
        self.habits = {habit.name: Habit(habit.name, habit.status) for habit in self.habits}

    def filter_by_status(self, status):
        return [habit for habit in self.habits.values() if habit.status == status]


async def item_drop(e, habit_list: HabitList):
    elements = ui.context.client.elements
    dragged = elements[int(e.args['id'][1:])]
    dragged.move(target_index=e.args['new_index'])

    habits = [x.habit for x in dragged.parent_slot.children if isinstance(x, components.HabitOrderCard) and x.habit]
    habit_list.order = [str(x.id) for x in habits]
    logger.info(f'New order: {habits}')


@ui.refreshable
def add_ui(habit_list: HabitList):
    with ui.column().classes('sortable').classes('gap-3'):
        for item in habit_list.habits:
            with components.HabitOrderCard(item):
                with ui.grid(columns=12, rows=1).classes('gap-0 items-center'):
                    name = HabitNameInput(item)
                    name.classes('col-span-3 col-3').props('borderless')

                    ui.space().classes('col-span-7')

                    star = HabitStarCheckbox(item, add_ui.refresh)
                    star.classes('col-span-1')

                    delete = HabitDeleteButton(item, habit_list, add_ui.refresh)
                    delete.classes('col-span-1')


def order_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes('w-full pl-1 items-center gap-3'):
            add_ui(habit_list)

            with components.HabitOrderCard():
                with ui.grid(columns=12, rows=1).classes('gap-0 items-center'):
                    add = HabitAddButton(habit_list, add_ui.refresh)
                    add.classes('col-span-12').props('borderless')

    ui.add_body_html(
        r'''<script type=