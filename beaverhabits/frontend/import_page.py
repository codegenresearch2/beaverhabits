import json

from nicegui import events, ui

from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

def parse_json_to_habit_list(text: str) -> HabitList:
    data = json.loads(text)
    habit_list = DictHabitList(data)
    if not habit_list.habits:
        raise ValueError("No habits found in the JSON data")
    return habit_list

def confirm_import_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label("Are you sure? All your current habits will be replaced or merged.")
        with ui.row():
            ui.button("Merge", on_click=lambda: dialog.submit("Merge"))
            ui.button("Replace", on_click=lambda: dialog.submit("Replace"))
            ui.button("Cancel", on_click=lambda: dialog.submit("Cancel"))
    return dialog

async def handle_import_upload(user: User, e: events.UploadEventArguments):
    dialog = confirm_import_dialog()
    result = await dialog

    if result == "Cancel":
        return

    try:
        text = e.content.read().decode("utf-8")
        imported_habit_list = parse_json_to_habit_list(text)

        if result == "Merge":
            merged_habit_list = await user_storage.merge_user_habit_list(user, imported_habit_list)
            await user_storage.save_user_habit_list(user, merged_habit_list)
            ui.notify(
                f"Merged {len(imported_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        elif result == "Replace":
            await user_storage.save_user_habit_list(user, imported_habit_list)
            ui.notify(
                f"Replaced with {len(imported_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
    except json.JSONDecodeError:
        ui.notify("Import failed: Invalid JSON", color="negative", position="top")
    except Exception as error:
        ui.notify(str(error), color="negative", position="top")

def import_ui_page(user: User):
    menu_header("Import", target=get_root_path())
    ui.upload(on_upload=lambda e: handle_import_upload(user, e), max_files=1).props("accept=.json")