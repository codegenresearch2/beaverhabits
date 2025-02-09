from nicegui import ui

from beaverhabits.frontend import components
from beaverhabits.frontend.components import (HabitAddButton, HabitDeleteButton, HabitNameInput, HabitStarCheckbox)
from beaverhabits.frontend.layout import layout
from beaverhabits.logging import logger
from beaverhabits.storage.storage import HabitList, HabitStatus


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
    logger.info(f'Item drop: {e.args['id']} -> {e.args['new_index']}')  # Updated logging message

    # Ensure the parent slot is not None before updating status
    assert dragged.parent_slot is not None, 'Dragged element has no parent slot'

    # Update habit status based on new position
    for idx, habit_id in enumerate(habit_list.order):
        habit = habit_list.habits.get(habit_id)
        if habit:
            habit.status = HabitStatus.ARCHIVED if idx >= len(habit_list.order) / 2 else HabitStatus.ACTIVE


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

                    # Conditionally render based on habit status
                    if habit_list.habits[item.name].status == 'archived':
                        ui.label(item.name).classes('text-gray-500 line-through')
                    else:
                        name


def order_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes('w-full pl-1 items-center gap-3'):
            add_ui(habit_list)

            with components.HabitOrderCard():
                with ui.grid(columns=12, rows=1).classes('gap-0 items-center'):
                    add = HabitAddButton(habit_list, add_ui.refresh)
                    add.classes('col-span-12').props('borderless')

    ui.add_body_html(
        r'''<script type="module">
        import '/statics/libs/sortable.min.js';
        document.addEventListener('DOMContentLoaded', () => {
            Sortable.create(document.querySelector('.sortable'), {
                animation: 150,
                ghostClass: 'opacity-50',
                onEnd: (evt) => emitEvent("item_drop", {id: evt.item.id, new_index: evt.newIndex }),
            });
        });
        </script>'''
    )
    ui.on('item_drop', lambda e: item_drop(e, habit_list))