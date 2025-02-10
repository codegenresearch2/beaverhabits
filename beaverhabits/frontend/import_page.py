import json
import logging

from nicegui import events, ui

from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

def convert_json_to_habit_list(text: str) -> HabitList:
    data = json.loads(text)
    habit_list = DictHabitList(data)
    if not habit_list.habits:
        raise ValueError("No habits found in the JSON data")
    return habit_list

def confirm_import_dialog(num_to_add: int, num_to_merge: int):
    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label(f"Are you sure? {num_to_add} habits will be added and {num_to_merge} habits will be merged.")
        with ui.row():
            ui.button("Confirm", on_click=lambda: dialog.submit("Confirm"))
            ui.button("Cancel", on_click=lambda: dialog.submit("Cancel"))
    return dialog

async def handle_import_upload(user: User, e: events.UploadEventArguments):
    try:
        text = e.content.read().decode("utf-8")
        imported_habit_list = convert_json_to_habit_list(text)

        current_habit_list = await user_storage.get_user_habit_list(user)
        if current_habit_list is None:
            current_habit_list = DictHabitList({"habits": []})

        added_habits = []
        merged_habits = []
        unchanged_habits = []

        for imported_habit in imported_habit_list.habits:
            existing_habit = next((h for h in current_habit_list.habits if h.id == imported_habit.id), None)
            if existing_habit is None:
                added_habits.append(imported_habit)
            elif existing_habit != imported_habit:
                merged_habits.append(imported_habit)
            else:
                unchanged_habits.append(imported_habit)

        dialog = confirm_import_dialog(len(added_habits), len(merged_habits))
        result = await dialog

        if result == "Confirm":
            current_habit_list.habits.extend(added_habits)
            for merged_habit in merged_habits:
                current_habit_list.habits = [merged_habit if h.id == merged_habit.id else h for h in current_habit_list.habits]
            await user_storage.save_user_habit_list(user, current_habit_list)

            logging.info(f"Imported {len(imported_habit_list.habits)} habits. Added: {len(added_habits)}, Merged: {len(merged_habits)}, Unchanged: {len(unchanged_habits)}")
            ui.notify(
                f"Imported {len(imported_habit_list.habits)} habits. Added: {len(added_habits)}, Merged: {len(merged_habits)}, Unchanged: {len(unchanged_habits)}",
                position="top",
                color="positive",
            )
    except json.JSONDecodeError:
        logging.error("Import failed: Invalid JSON")
        ui.notify("Import failed: Invalid JSON", color="negative", position="top")
    except Exception as error:
        logging.error(f"Import failed: {str(error)}")
        ui.notify(str(error), color="negative", position="top")

def import_ui_page(user: User):
    menu_header("Import", target=get_root_path())
    ui.upload(on_upload=lambda e: handle_import_upload(user, e), max_files=1).props("accept=.json")
    return