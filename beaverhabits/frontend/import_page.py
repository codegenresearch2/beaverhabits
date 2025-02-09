import json
import logging
from nicegui import events, ui
from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

def import_from_json(text: str) -> HabitList:
    try:
        d = json.loads(text)
        habit_list = DictHabitList(d)
        if not habit_list.habits:
            raise ValueError("No habits found")
        return habit_list
    except json.JSONDecodeError:
        logging.exception("Invalid JSON during import")
        raise
    except Exception as e:
        logging.exception("Error during import")
        raise ValueError(f"Error during import: {str(e)}")

async def import_ui_page(user: User):
    habit_list = await user_storage.get_user_habit_list(user)
    existing_habit_names = {habit.name for habit in habit_list.habits} if habit_list else set()

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
            to_habit_list = import_from_json(text)

            added_habits = []
            merged_habits = []
            unchanged_habits = []

            for habit in to_habit_list.habits:
                if habit.name not in existing_habit_names:
                    added_habits.append(habit)
                else:
                    merged_habits.append(habit)
                    existing_habit_names.remove(habit.name)
                unchanged_habits.append(habit)

            if added_habits or merged_habits:
                ui.notify(
                    f"Imported {len(added_habits)} new habits and merged {len(merged_habits)} existing habits",
                    position="top",
                    color="positive",
                )
            else:
                ui.notify("No new habits to add or merge.", position="top", color="neutral")

        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            ui.notify(str(error), color="negative", position="top")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return