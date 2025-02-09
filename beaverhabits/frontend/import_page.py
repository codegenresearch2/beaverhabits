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
            imported_habits = await import_from_json(text)
            existing_habit_list = await user_storage.get_user_habit_list(user)

            if existing_habit_list is None:
                existing_habit_list = DictHabitList({'habits': []})

            # Use sets for added and merged habits to simplify logic
            existing_ids = {habit['id'] for habit in existing_habit_list.habits}
            new_ids = {habit['id'] for habit in imported_habits.habits}
            added_ids = new_ids - existing_ids
            merged_ids = existing_ids & new_ids
            unchanged_ids = new_ids - added_ids - merged_ids

            added_habits = [habit for habit in imported_habits.habits if habit['id'] in added_ids]
            merged_habits = [habit for habit in imported_habits.habits if habit['id'] in merged_ids]
            unchanged_habits = [habit for habit in imported_habits.habits if habit['id'] in unchanged_ids]

            # Log the results
            logging.info(f"Added {len(added_habits)} habits, Merged {len(merged_habits)} habits, Unchanged {len(unchanged_habits)} habits")

            # Save the new habit list
            await user_storage.save_user_habit_list(user, imported_habits)
            ui.notify(
                f"Imported {len(imported_habits.habits)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(error)
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return