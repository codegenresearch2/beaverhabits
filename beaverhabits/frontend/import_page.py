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
            other = await import_from_json(text)
            current = await get_current_habit_list()

            to_add = set(other.habits) - set(current.habits)
            to_merge = set(other.habits) & set(current.habits)
            unchanged = set(current.habits) - set(other.habits)

            logging.info(f"To add: {len(to_add)}, to merge: {len(to_merge)}, unchanged: {len(unchanged)}")

            with ui.dialog() as dialog, ui.card().classes("w-64"):
                ui.label(f"Are you sure? {len(to_add)} habits will be added and {len(to_merge)} habits will be merged.")
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            result = await dialog
            if result != "Yes":
                return

            merged_habit_list = await user_storage.merge_user_habit_list(user, other)
            await user_storage.save_user_habit_list(user, merged_habit_list)

            ui.notify(
                f"Imported and merged {len(to_add) + len(to_merge)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError as e:
            logging.error(f"Import failed: Invalid JSON - {str(e)}")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.error(f"Import failed: {str(error)}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return