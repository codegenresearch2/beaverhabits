from nicegui import ui
from beaverhabits.frontend.components import HabitAddButton, HabitDeleteButton, HabitStarCheckbox, HabitAddCard, HabitNameInput
from beaverhabits.frontend.layout import layout
from beaverhabits.storage.storage import HabitList
from beaverhabits.logging import logger

grid_classes = "w-full gap-0 items-center"

def validate_habit_name(name):
    if not name:
        raise ValueError("Habit name cannot be empty")
    return name

@ui.refreshable
def habit_item(item, habit_list):
    with HabitAddCard(item, habit_list, habit_item.refresh):
        name = HabitNameInput(item)
        name.classes("col-span-7 break-all")

        star = HabitStarCheckbox(item, habit_item.refresh)
        star.props("flat fab-mini color=grey")
        star.classes("col-span-1")

        delete = HabitDeleteButton(item, habit_list, habit_item.refresh)
        delete.props("flat fab-mini color=grey")
        delete.classes("col-span-1")

@ui.refreshable
def add_ui(habit_list: HabitList):
    for item in habit_list.habits:
        habit_item(item, habit_list)

@ui.refreshable
def add_page_ui(habit_list: HabitList):
    with layout():
        with ui.column().classes("w-full pl-1 items-center"):
            add_ui(habit_list)

            with ui.grid(columns=9, rows=1).classes(grid_classes):
                add = HabitAddButton(habit_list, add_ui.refresh)
                add.classes("col-span-7")

@ui.page('/')
def index():
    habit_list = HabitList()
    add_page_ui(habit_list)

@ui.page('/habits/{habit_id}')
def habit_page(habit_id: str):
    habit = HabitList().get_habit_by_id(habit_id)
    # Add habit page UI components here

@ui.page('/add')
def add_habit_page():
    habit_list = HabitList()
    add_page_ui(habit_list)

@ui.page('/settings')
def settings_page():
    # TODO: Add settings page UI components here
    pass

@ui.page('/about')
def about_page():
    # TODO: Add about page UI components here
    pass

async def item_drop(e):
    logger.info(f"Item dropped: {e.args}")
    # TODO: Add logic to handle item drop event

# Add JavaScript snippet for handling sortable functionality
ui.add_head_html("""
<script>
// JavaScript code for handling sortable functionality
</script>
""")

ui.run(title='Beaver Habits')