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


async def import_ui_page(user: User):
    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label("Are you sure? All your current habits will be replaced.")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))

    async def handle_upload(e: events.UploadEventArguments):
        try:
            result = await dialog
            if result != "Yes":
                return

            text = e.content.read().decode("utf-8")
            to_habit_list = await import_from_json(text)
            existing_habit_list = await user_storage.get_user_habit_list(user)

            # Use sets for added and merged habits to simplify logic
            added_habits_set = set(habit['id'] for habit in to_habit_list.habits)
            merged_habits_set = set(habit['id'] for habit in existing_habit_list.habits) & added_habits_set
            unchanged_habits_set = added_habits_set - merged_habits_set

            added_habits = [habit for habit in to_habit_list.habits if habit['id'] in added_habits_set]
            merged_habits = [habit for habit in to_habit_list.habits if habit['id'] in merged_habits_set]
            unchanged_habits = [habit for habit in to_habit_list.habits if habit['id'] in unchanged_habits_set]

            # Log the results
            logging.info(f"Added {len(added_habits)} habits")
            logging.info(f"Merged {len(merged_habits)} habits")
            logging.info(f"Unchanged {len(unchanged_habits)} habits")

            # Save the new habit list
            await user_storage.save_user_habit_list(user, to_habit_list)
            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
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