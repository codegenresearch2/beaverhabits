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
        raise ValueError("No habits found in the imported data")
    return habit_list

async def merge_habits(user: User, imported_habits: HabitList):
    current_habits = await user_storage.get_user_habit_list(user)
    if current_habits is None:
        await user_storage.save_user_habit_list(user, imported_habits)
        logging.info(f"Imported {len(imported_habits.habits)} new habits")
    else:
        merged_habits = await user_storage.merge_user_habit_list(user, imported_habits)
        added_habits = set(imported_habits.habits) - set(current_habits.habits)
        merged_count = len(set(current_habits.habits) & set(imported_habits.habits))
        unchanged_habits = set(current_habits.habits) - set(imported_habits.habits)
        logging.info(f"Imported {len(added_habits)} new habits: {added_habits}")
        logging.info(f"Merged {merged_count} habits")
        logging.info(f"{len(unchanged_habits)} habits remained unchanged: {unchanged_habits}")

def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        try:
            imported_habits = await import_from_json(e.content.read().decode("utf-8"))
            current_habits = await user_storage.get_user_habit_list(user)
            if current_habits is None:
                message = f"Are you sure? All your current habits will be replaced with {len(imported_habits.habits)} habits."
            else:
                added_habits = set(imported_habits.habits) - set(current_habits.habits)
                merged_count = len(set(current_habits.habits) & set(imported_habits.habits))
                unchanged_habits = set(current_habits.habits) - set(imported_habits.habits)
                message = f"Are you sure? {len(added_habits)} new habits will be added, {merged_count} habits will be merged, and {len(unchanged_habits)} habits will remain unchanged."

            with ui.dialog() as dialog, ui.card().classes("w-64"):
                ui.label(message)
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            if await dialog != "Yes":
                return

            await merge_habits(user, imported_habits)
            ui.notify(f"Imported {len(imported_habits.habits)} habits", position="top", color="positive")
        except json.JSONDecodeError:
            logging.exception("Import failed: Invalid JSON")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(f"Import failed: {str(error)}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")