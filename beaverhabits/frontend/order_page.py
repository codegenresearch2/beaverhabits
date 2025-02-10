from enum import Enum
from nicegui import ui

from beaverhabits.frontend import components
from beaverhabits.frontend.components import HabitAddButton, HabitDeleteButton, HabitNameInput
from beaverhabits.frontend.layout import layout
from beaverhabits.logging import logger
from beaverhabits.storage.storage import HabitList

class HabitStatus(Enum):
    ACTIVE = 'active'
    ARCHIVED = 'archived'

async def item_drop(e, habit_list: HabitList):
    elements = ui.context.client.elements
    dragged = elements[int(e.args["id"][1:])]
    dragged.move(target_index=e.args["new_index"])

    habits = [
        x.habit
        for x in dragged.parent_slot.children
        if isinstance(x, components.HabitOrderCard) and x.habit
    ]
    habit_list.order = [str(x.id) for x in habits]
    habit_list.update_habit_status(habits)
    logger.info(f"Item dropped: {dragged.habit.name}, New index: {e.args['new_index']}")
    add_ui.refresh()

@ui.refreshable
def add_ui(habit_list: HabitList):
    with ui.column().classes("sortable").classes("gap-3"):
        for item in habit_list.habits:
            with components.HabitOrderCard(item):
                with ui.grid(columns=12, rows=1).classes("gap-0 items-center"):
                    if item.status == HabitStatus.ARCHIVED:
                        name = ui.label(item.name)
                        name.classes("col-span-10 col-10")
                    else:
                        name = HabitNameInput(item)
                        name.classes("col-span-3 col-3")
                    name.props("borderless")

                    delete = HabitDeleteButton(item, habit_list, add_ui.refresh)
                    delete.classes("col-span-2")

def order_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center gap-3"):
            add_ui(habit_list)

            with components.HabitOrderCard():
                with ui.grid(columns=12, rows=1).classes("gap-0 items-center"):
                    add = HabitAddButton(habit_list, add_ui.refresh)
                    add.classes("col-span-12")
                    add.props("borderless")

    ui.add_body_html(
        r"""
        <script type="module">
        import '/statics/libs/sortable.min.js';
        document.addEventListener('DOMContentLoaded', () => {
            Sortable.create(document.querySelector('.sortable'), {
                animation: 150,
                ghostClass: 'opacity-50',
                onEnd: (evt) => emitEvent("item_drop", {id: evt.item.id, new_index: evt.newIndex }),
            });
        });
        </script>
    """
    )
    ui.on("item_drop", lambda e: item_drop(e, habit_list))