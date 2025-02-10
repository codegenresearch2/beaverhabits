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
        raise ValueError("No habits found")
    return habit_list

def import_ui_page(user: User):
    logging.info("Import UI page accessed")

    async def get_current_habit_list():
        current_habit_list = await user_storage.get_user_habit_list(user)
        if current_habit_list is None:
            current_habit_list = DictHabitList({"habits": []})
        return current_habit_list

    async def handle_upload(e: events.UploadEventArguments):
        try:
            text = e.content.read().decode("utf-8")
            from_habit_list = await import_from_json(text)
            to_habit_list = await get_current_habit_list()

            habits_to_add = set(from_habit_list.habits) - set(to_habit_list.habits)
            habits_to_merge = set(from_habit_list.habits) & set(to_habit_list.habits)
            unchanged_habits = set(to_habit_list.habits) - set(from_habit_list.habits)

            logging.info(f"Habits to add: {len(habits_to_add)}, Habits to merge: {len(habits_to_merge)}, Unchanged habits: {len(unchanged_habits)}")

            with ui.dialog() as dialog, ui.card().classes("w-64"):
                ui.label(f"Are you sure? {len(habits_to_add)} habits will be added and {len(habits_to_merge)} habits will be merged.")
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            result = await dialog
            if result != "Yes":
                return

            merged_habit_list = await user_storage.merge_user_habit_list(user, from_habit_list)
            await user_storage.save_user_habit_list(user, merged_habit_list)

            ui.notify(
                f"Imported and merged {len(habits_to_add) + len(habits_to_merge)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            logging.exception("Import failed: Invalid JSON")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception("Import failed")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload functionality: allows users to upload a JSON file containing habits
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return