import json
import logging

from nicegui import events, ui

from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

def import_from_json(text: str) -> HabitList:
    data = json.loads(text)
    habit_list = DictHabitList(data)
    if not habit_list.habits:
        raise ValueError("No habits found in the JSON data")
    return habit_list

async def handle_import_upload(user: User, e: events.UploadEventArguments):
    try:
        text = e.content.read().decode("utf-8")
        imported_habit_list = import_from_json(text)

        current_habit_list = await user_storage.get_user_habit_list(user)
        if current_habit_list is None:
            current_habit_list = DictHabitList({"habits": []})

        imported_habits = set(imported_habit_list.habits)
        current_habits = set(current_habit_list.habits)

        added_habits = imported_habits - current_habits
        merged_habits = imported_habits & current_habits
        unchanged_habits = current_habits - imported_habits

        with ui.dialog() as dialog, ui.card().classes("w-64"):
            ui.label(f"Are you sure? {len(added_habits)} habits will be added and {len(merged_habits)} habits will be merged.")
            with ui.row():
                ui.button("Confirm", on_click=lambda: dialog.submit("Confirm"))
                ui.button("Cancel", on_click=lambda: dialog.submit("Cancel"))

        result = await dialog

        if result == "Confirm":
            current_habit_list.habits = list(current_habits | added_habits | merged_habits)
            await user_storage.save_user_habit_list(user, current_habit_list)

            logging.info(f"Imported {len(imported_habits)} habits. Added: {len(added_habits)}, Merged: {len(merged_habits)}, Unchanged: {len(unchanged_habits)}")
            ui.notify(
                f"Imported {len(imported_habits)} habits. Added: {len(added_habits)}, Merged: {len(merged_habits)}, Unchanged: {len(unchanged_habits)}",
                position="top",
                color="positive",
            )
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