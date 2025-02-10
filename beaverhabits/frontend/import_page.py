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

async def merge_habits(user: User, other: HabitList):
    current = await user_storage.get_user_habit_list(user)
    if current is None:
        await user_storage.save_user_habit_list(user, other)
        logging.info(f"Imported {len(other.habits)} new habits")
    else:
        merged = await user_storage.merge_user_habit_list(user, other)
        added = set(other.habits) - set(current.habits)
        merged_count = len(set(current.habits) & set(other.habits))
        unchanged = set(current.habits) - set(other.habits)
        logging.info(f"Imported {len(added)} new habits, merged {merged_count} habits, and {len(unchanged)} habits remained unchanged")

def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        try:
            other = await import_from_json(e.content.read().decode("utf-8"))
            current = await user_storage.get_user_habit_list(user)
            message = f"Are you sure? This will replace your current habits with {len(other.habits)} habits."
            if current is not None:
                added = set(other.habits) - set(current.habits)
                merged_count = len(set(current.habits) & set(other.habits))
                unchanged = set(current.habits) - set(other.habits)
                message = f"Are you sure? {len(added)} new habits will be added, {merged_count} habits will be merged, and {len(unchanged)} habits will remain unchanged."

            with ui.dialog() as dialog, ui.card().classes("w-64"):
                ui.label(message)
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            if await dialog != "Yes":
                return

            await merge_habits(user, other)
            ui.notify(f"Imported {len(other.habits)} habits", position="top", color="positive")
        except json.JSONDecodeError:
            logging.exception("Import failed: Invalid JSON")
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception(f"Import failed: {error}")
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return