import logging\nfrom nicegui import ui\nfrom beaverhabits.frontend.components import (HabitAddButton, HabitDeleteButton, HabitNameInput, HabitStarCheckbox)\nfrom beaverhabits.frontend.layout import layout\nfrom beaverhabits.storage.storage import HabitList\n\nlogger = logging.getLogger(__name__)\n\n@ui.refreshable\n\ndef add_ui(habit_list: HabitList):\n    for item in habit_list.habits:\n        with ui.grid(columns=9, rows=1).classes('w-full gap-0 items-center'):\n            name = HabitNameInput(item)\n            name.classes('col-span-7 break-all')\n\n            star = HabitStarCheckbox(item, add_ui.refresh)\n            star.props('flat fab-mini color=grey')\n            star.classes('col-span-1')\n\n            delete = HabitDeleteButton(item, habit_list, add_ui.refresh)\n            delete.props('flat fab-mini color=grey')\n            delete.classes('col-span-1')\n\n\ndef add_page_ui(habit_list: HabitList):\n    with layout():\n        with ui.column().classes('w-full pl-1 items-center'):\n            add_ui(habit_list)\n\n            with ui.grid(columns=9, rows=1).classes('w-full gap-0 items-center'):\n                add = HabitAddButton(habit_list, add_ui.refresh)\n                add.classes('col-span-7')