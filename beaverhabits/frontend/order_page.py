from nicegui import ui

from beaverhabits.frontend import components
from beaverhabits.frontend.components import HabitAddButton, HabitDeleteButton, HabitNameInput
from beaverhabits.frontend.layout import layout
from beaverhabits.logging import logger
from beaverhabits.storage.storage import HabitList, HabitStatus

async def item_drop(e, habit_list: HabitList):
    logger.info(f"Item dropped: {e.args['id']} to index {e.args['new_index']}")
    elements = ui.context.client.elements
    dragged = elements[int(e.args["id"][1:])]
    dragged.move(target_index=e.args["new_index"])

    assert dragged.parent_slot is not None
    habits = [
        x.habit
        for x in dragged.parent_slot.children
        if isinstance(x, components.HabitOrderCard) and x.habit
    ]
    habit_list.order = [str(x.id) for x in habits]

    if e.args['new_index'] == 0:
        dragged.habit.status = HabitStatus.UNARCHIVED
    elif e.args['new_index'] == len(habits) - 1:
        dragged.habit.status = HabitStatus.ARCHIVED
    else:
        if habits[e.args['new_index'] - 1].status == HabitStatus.ARCHIVED or habits[e.args['new_index'] + 1].status == HabitStatus.ARCHIVED:
            dragged.habit.status = HabitStatus.ARCHIVED
        else:
            dragged.habit.status = HabitStatus.UNARCHIVED

    logger.info(f"New order: {habits}")
    add_ui.refresh()

@ui.refreshable
def add_ui(habit_list: HabitList):
    with ui.column().classes("sortable").classes("gap-3"):
        for item in habit_list.habits:
            with components.HabitOrderCard(item):
                with ui.grid(columns=12, rows=1).classes("gap-0 items-center"):
                    if item.status == HabitStatus.UNARCHIVED:
                        name = HabitNameInput(item)
                    else:
                        name = ui.label(item.name)
                    name.classes("col-span-9")
                    name.props("borderless")

                    ui.space().classes("col-span-1")

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