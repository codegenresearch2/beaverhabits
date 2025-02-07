from nicegui import ui\\nfrom beaverhabits.frontend import components\\\\nfrom beaverhabits.frontend.components import (\\\\n    HabitAddButton, HabitDeleteButton, HabitNameInput, HabitStarCheckbox)\\\\nfrom beaverhabits.frontend.layout import layout\\\\nfrom beaverhabits.logging import logger\\\\nfrom beaverhabits.storage.storage import HabitList\\\n\\\\nclass Habit:\\\\ndef __init__(self, name, status=None):\\\\\n    self.name = name\\\\\n    self.status = status or 'active'\\\\n\\\\nclass DictHabit(Habit):\\\\\ndef __init__(self, name, status=None):\\\\\n    super().__init__(name, status)\\\\n\\\\nclass HabitList:\\\\\ndef __init__(self, habits=None, order=None):\\\\\n    self.habits = habits or []\\\\n    self.order = order or []\\\\n\\\\nclass DictHabitList(HabitList):\\\\\ndef __init__(self, habits=None, order=None):\\\\\n    super().__init__(habits, order)\\\\n\\\\nasync def item_drop(e, habit_list: HabitList):\\\\\nelements = ui.context.client.elements\\\\\ndragged = elements[int(e.args['id'][1:])]\\\\\ndragged.move(target_index=e.args['new_index'])\\\\\nhabits = [x.habit for x in dragged.parent_slot.children if isinstance(x, components.HabitOrderCard) and x.habit]\\\\\nhabit_list.order = [str(x.id) for x in habits]\\\\\nlogger.info(f'New order: {habits}')\\\\\n\\\\n@ui.refreshable\\\\ndef add_ui(habit_list: HabitList):\\\\\n    with ui.column().classes('sortable').classes('gap-3'):\\\\\n        for item in habit_list.habits:\\\\\n            with components.HabitOrderCard(item) if item.status == 'active' else ui.card():\\\\\n                with ui.grid(columns=12, rows=1).classes('gap-0 items-center'):\\\\\n                    name = HabitNameInput(item) if item.status == 'active' else ui.label(item.name).classes('col-span-3 col-3')\\\\\n                    name.classes('col-span-3 col-3').props('borderless')\\\\\n                    ui.space().classes('col-span-7')\\\\\n                    star = HabitStarCheckbox(item, add_ui.refresh) if item.status == 'active' else None\\\\\n                    if star:\\\\\n                        star.classes('col-span-1')\\\\\n                    delete = HabitDeleteButton(item, habit_list, add_ui.refresh) if item.status == 'active' else None\\\\\n                    if delete:\\\\\n                        delete.classes('col-span-1')\\\\\n\\\\nclass HabitOrderCard(ui.card):\\\\\ndef __init__(self, habit=None):\\\\\n    super().__init__()\\\\\n    self.habit = habit\\\\\n\\\\n\\\\ndef order_page_ui(habit_list: HabitList):\\\\\n    with layout():\\\\\n        with ui.column().classes('w-full pl-1 items-center gap-3'):\\\\\n            add_ui(habit_list)\\\\\n            with HabitOrderCard() if habit_list.habits else ui.card():\\\\\n                with ui.grid(columns=12, rows=1).classes('gap-0 items-center'):\\\\\n                    add = HabitAddButton(habit_list, add_ui.refresh) if habit_list.habits else None\\\\\n                    if add:\\\\\n                        add.classes('col-span-12').props('borderless')\\\\\n    ui.add_body_html(\\\