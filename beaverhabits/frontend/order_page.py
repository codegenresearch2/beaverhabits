from nicegui import ui

from beaverhabits.frontend import components
from beaverhabits.frontend.components import (
    HabitAddButton,
    HabitDeleteButton,
    HabitNameInput,
    HabitStarCheckbox,
)
from beaverhabits.frontend.layout import layout
from beaverhabits.logging import logger
from beaverhabits.storage.storage import HabitList

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
    logger.info(f"New order: {habits}, New status: {[habit.status for habit in habits]}")
    add_ui.refresh()

@ui.refreshable
def add_ui(habit_list: HabitList):
    with ui.column().classes("sortable").classes("gap-3"):
        for item in habit_list.habits:
            with components.HabitOrderCard(item):
                with ui.grid(columns=12, rows=1).classes("gap-0 items-center"):
                    if item.status == 'completed':
                        name = ui.label(item.name)
                    else:
                        name = HabitNameInput(item)
                    name.classes("col-span-3 col-3")
                    name.props("borderless")

                    ui.space().classes("col-span-6")

                    star = HabitStarCheckbox(item, add_ui.refresh)
                    star.classes("col-span-1")

                    status_label = ui.label(item.status)
                    status_label.classes("col-span-1")

                    delete = HabitDeleteButton(item, habit_list, add_ui.refresh)
                    delete.classes("col-span-1")

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