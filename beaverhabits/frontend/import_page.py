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
    return HabitList(habit_list.data)

async def merge_habits(user: User, to_habit_list: HabitList):
    current_habit_list = await user_storage.get_user_habit_list(user)
    if current_habit_list is None:
        await user_storage.save_user_habit_list(user, to_habit_list)
        logging.info(f"Imported {len(to_habit_list.habits)} new habits")
    else:
        current_habits = set(current_habit_list.habits)
        to_habits = set(to_habit_list.habits)
        added = to_habits - current_habits
        merged = current_habits & to_habits
        unchanged = current_habits - to_habits
        current_habit_list.habits = list(current_habits | to_habits)
        await user_storage.save_user_habit_list(user, current_habit_list)
        logging.info(f"Imported {len(added)} new habits, merged {len(merged)} habits, and {len(unchanged)} habits were unchanged")

def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        try:
            text = e.content.read().decode("utf-8")
            to_habit_list = await import_from_json(text)
            current_habit_list = await user_storage.get_user_habit_list(user)
            if current_habit_list is None:
                message = f"Are you sure? All your current habits will be replaced with {len(to_habit_list.habits)} habits."
            else:
                current_habits = set(current_habit_list.habits)
                to_habits = set(to_habit_list.habits)
                added = to_habits - current_habits
                merged = current_habits & to_habits
                unchanged = len(current_habits) - len(merged)
                message = f"Are you sure? {len(added)} new habits will be added, {len(merged)} habits will be merged, and {unchanged} habits will remain unchanged."

            with ui.dialog() as dialog, ui.card().classes("w-64"):
                ui.label(message)
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            result = await dialog
            if result != "Yes":
                return

            await merge_habits(user, to_habit_list)
            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            logging.exception("Import failed: Invalid JSON")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(f"Import failed: {str(error)}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return