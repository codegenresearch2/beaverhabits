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
    d = json.loads(text)
    habit_list = DictHabitList(d)
    if not habit_list.habits:
        raise ValueError("No habits found")
    return habit_list


def import_ui_page(user: User):
    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label("Are you sure? All your current habits will be replaced.")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))

    def handle_upload(e: events.UploadEventArguments):
        try:
            result = dialog.result
            if result != "Yes":
                return

            text = e.content.read().decode("utf-8")
            to_habit_list = import_from_json(text)
            existing_habit_list = user_storage.get_user_habit_list(user)

            if existing_habit_list is None:
                user_storage.save_user_habit_list(user, to_habit_list)
                ui.notify(
                    f"Imported {len(to_habit_list.habits)} habits",
                    position="top",
                    color="positive",
                )
            else:
                added_habits = 0
                merged_habits = 0
                existing_habit_set = set(existing_habit_list.habits)
                to_habit_set = set(to_habit_list.habits)

                for habit in to_habit_set:
                    if habit not in existing_habit_set:
                        added_habits += 1
                    else:
                        merged_habits += 1

                if added_habits > 0 or merged_habits > 0:
                    user_storage.merge_user_habit_list(user, to_habit_list)
                    ui.notify(
                        f"Imported and merged {added_habits + merged_habits} habits",
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