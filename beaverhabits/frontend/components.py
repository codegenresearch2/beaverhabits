import calendar\\nimport datetime\\nfrom contextlib import contextmanager\\nfrom nicegui import ui\\nfrom beaverhabits.frontend.components import CalendarHeatmap, HabitDateInput, habit_heat_map\\nfrom beaverhabits.frontend.css import CALENDAR_CSS, CHECK_BOX_CSS\\nfrom beaverhabits.frontend.layout import layout\\nfrom beaverhabits.storage.meta import get_habit_heatmap_path\\nfrom beaverhabits.storage.storage import Habit\\nWEEKS_TO_DISPLAY = 15\\n\\n@contextmanager\\ndef card():\\n    with ui.card().classes('p-3 gap-0 no-shadow items-center') as card:\\n        card.classes('w-full')\\n        card.style('max-width: 350px')\\n        yield\\n\\ndef habit_page(today: datetime.date, habit: Habit):\\n    ticked_data = {x: True for x in habit.ticked_days}\\n    habit_calendar = CalendarHeatmap.build(today, WEEKS_TO_DISPLAY, calendar.MONDAY)\\n\\n    with card():\\n        HabitDateInput(today, habit, ticked_data)\\n\\n    with card():\\n        link('Last 3 Months', get_habit_heatmap_path(habit)).classes('text-base')\\n        habit_heat_map(habit, habit_calendar, ticked_data=ticked_data)\\n\\ndef habit_page_ui(today: datetime.date, habit: Habit):\\n    ui.add_css(CHECK_BOX_CSS)\\n    ui.add_css(CALENDAR_CSS)\\n\\n    with layout(title=habit.name):\\n        habit_page(today, habit)