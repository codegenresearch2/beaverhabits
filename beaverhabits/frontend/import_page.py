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
    d = json.loads(text)
    habit_list = DictHabitList(d)
    if not habit_list.habits:
        raise ValueError("No habits found")
    return habit_list

def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        try:
            text = e.content.read().decode("utf-8")
            to_habit_list = await import_from_json(text)
            existing_habit_list = await user_storage.get_user_habit_list(user)
            if existing_habit_list:
                added, merged, unchanged = existing_habit_list.calculate_import_stats(to_habit_list)
                logging.info(f"Added: {added}, Merged: {merged}, Unchanged: {unchanged}")
                await existing_habit_list.merge(to_habit_list)
            else:
                await user_storage.save_user_habit_list(user, to_habit_list)
                logging.info("Habits imported successfully.")
            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            logging.exception("Invalid JSON during import.")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(f"An error occurred during import: {error}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")