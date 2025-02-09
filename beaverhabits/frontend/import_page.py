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
    habit_list = DictHabitList(json.loads(text))
    if not habit_list.habits:
        raise ValueError("No habits found")
    return habit_list

def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        text = e.content.read().decode("utf-8")
        try:
            to_habit_list = await import_from_json(text)

            current_habit_list = await user_storage.get_user_habit_list(user)
            if current_habit_list is None:
                current_habit_list = DictHabitList({"habits": []})

            # Determine what habits will be added, merged, or unchanged
            current_ids = {habit['id'] for habit in current_habit_list.habits}
            to_ids = {habit['id'] for habit in to_habit_list.habits}

            added_ids = to_ids - current_ids
            merged_ids = to_ids & current_ids
            unchanged_ids = to_ids & current_ids

            added_habits = [habit for habit in to_habit_list.habits if habit['id'] in added_ids]
            merged_habits = [habit for habit in to_habit_list.habits if habit['id'] in merged_ids]
            unchanged_habits = [habit for habit in current_habit_list.habits if habit['id'] in unchanged_ids]

            # Log the results
            logging.info(f"Added {len(added_habits)} habits, merged {len(merged_habits)} habits, unchanged {len(unchanged_habits)} habits")

            # Merge the new habits with the existing habits
            if added_habits or merged_habits:
                updated_habit_list = await user_storage.merge_user_habit_list(user, to_habit_list)
                await user_storage.save_user_habit_list(user, updated_habit_list)
            else:
                ui.notify("No new habits added.", position="top", color="neutral")

            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(f"An error occurred during import: {error}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return