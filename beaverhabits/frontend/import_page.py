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
        raise ValueError("Invalid JSON")
    except Exception as e:
        logging.exception("Error during import")
        raise ValueError(f"Error during import: {str(e)}")

def import_ui_page(user: User):
    habit_list = user_storage.get_user_habit_list(user)
    existing_habit_names = {habit.name for habit in habit_list.habits} if habit_list else set()

    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label(f"Are you sure? All your current habits will be replaced. ({len(existing_habit_names)} habits will be replaced)")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))

    result = dialog.submit()
    if result != "Yes":
        return

    def handle_upload(e: events.UploadEventArguments):
        try:
            text = e.content.read().decode("utf-8")
            to_habit_list = import_from_json(text)

            added_habits = [habit for habit in to_habit_list.habits if habit.name not in existing_habit_names]
            merged_habits = [habit for habit in to_habit_list.habits if habit.name in existing_habit_names]
            unchanged_habits = [habit for habit in to_habit_list.habits if habit in (added_habits + merged_habits)]

            logging.info(f"Imported {len(added_habits)} new habits and merged {len(merged_habits)} existing habits")

            if added_habits or merged_habits:
                user_storage.save_user_habit_list(user, to_habit_list)
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