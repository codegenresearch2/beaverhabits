import json
import logging

from nicegui import events, ui

from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

async def import_from_json(text: str) -> HabitList:
    data = json.loads(text)
    habit_list = DictHabitList(data)
    if not habit_list.habits:
        raise ValueError("No habits found in the JSON data")
    return habit_list

async def handle_import_upload(user: User, e: events.UploadEventArguments):
    try:
        text = e.content.read().decode("utf-8")
        other = await import_from_json(text)

        current = await user_storage.get_user_habit_list(user) or DictHabitList({"habits": []})

        merged = await user_storage.merge_user_habit_list(user, other)

        with ui.dialog() as dialog, ui.card().classes("w-64"):
            ui.label(f"Are you sure? {len(merged.habits) - len(current.habits)} habits will be added or merged.")
            with ui.row():
                ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                ui.button("No", on_click=lambda: dialog.submit("No"))

        result = await dialog

        if result == "Yes":
            await user_storage.save_user_habit_list(user, merged)
            logging.info(f"Imported {len(merged.habits)} habits")
            ui.notify(f"Imported {len(merged.habits)} habits", position="top", color="positive")
    except json.JSONDecodeError:
        logging.error("Import failed: Invalid JSON")
        ui.notify("Import failed: Invalid JSON", color="negative", position="top")
    except Exception as error:
        logging.exception("Import failed")
        ui.notify(str(error), color="negative", position="top")

def import_ui_page(user: User):
    menu_header("Import", target=get_root_path())
    ui.upload(on_upload=lambda e: handle_import_upload(user, e), max_files=1).props("accept=.json")
    return