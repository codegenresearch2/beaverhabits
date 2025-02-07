from nicegui import ui\" from beaverhabits.frontend.components import (\n    HabitAddButton, HabitDeleteButton, HabitNameInput, HabitStarCheckbox, HabitAddCard\n) \nfrom beaverhabits.frontend.layout import layout\nfrom beaverhabits.storage.storage import HabitList\n\nclass HabitAddCard(ui.card):\n    def __init__(self, item, *args, **kwargs):\n        super().__init__(*args, **kwargs)\n        self.classes('p-3 gap-0 no-shadow items-center')\n        self.style('max-width: 350px')\n        self.classes('w-full')\\"    def _render(self, item):\n        with self:\n            name = HabitNameInput(item)\n            name.classes('col-span-7 break-all')\n\n            star = HabitStarCheckbox(item, add_ui.refresh)\n            star.props('flat fab-mini color=grey')\n            star.classes('col-span-1')\n\n            delete = HabitDeleteButton(item, habit_list, add_ui.refresh)\n            delete.props('flat fab-mini color=grey')\n            delete.classes('col-span-1')\\\n@ui.refreshable\ndef add_ui(habit_list: HabitList):\n    for item in habit_list.habits:\n        card = HabitAddCard(item)\n        card.classes('w-full')\\\n\ndef add_page_ui(habit_list: HabitList):\n    with layout():\n        with ui.column().classes('w-full pl-1 items-center'):\n            add_ui(habit_list)\n\n            with ui.grid(columns=9, rows=1).classes('w-full gap-0 items-center'):\n                add = HabitAddButton(habit_list, add_ui.refresh)\n                add.classes('col-span-7')\n                add_card = HabitAddCard(add, habit_list, add_ui.refresh)\n                add_card.classes('w-full')