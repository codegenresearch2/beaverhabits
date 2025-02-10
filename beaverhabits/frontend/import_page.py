import json
import logging
from nicegui import events, ui
from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.views import user_storage

# Configure logging
logging.basicConfig(level=logging.INFO)

def import_from_json(text: str) -> HabitList:
    try:
        d = json.loads(text)
        habit_list = DictHabitList(d)
        if not habit_list.habits:
            raise ValueError("No habits found")
        return habit_list
    except json.JSONDecodeError:
        logging.exception("Invalid JSON")
        raise
    except Exception as e:
        logging.exception(f"Error importing habits: {e}")
        raise

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
            to_habit_list = import_from_json(text)
            existing_habit_list = await user_storage.get_user_habit_list(user)

            if existing_habit_list is None:
                await user_storage.save_user_habit_list(user, to_habit_list)
                logging.info(f"Imported {len(to_habit_list.habits)} habits")
            else:
                merged_habit_list = await existing_habit_list.merge(to_habit_list)
                await user_storage.save_user_habit_list(user, merged_habit_list)
                added_count = len([habit for habit in to_habit_list.habits if habit not in existing_habit_list.habits])
                merged_count = len([habit for habit in to_habit_list.habits if habit in existing_habit_list.habits])
                logging.info(f"Imported {added_count} added and {merged_count} merged habits")

            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
            logging.exception("Invalid JSON")
        except Exception as e:
            ui.notify(str(e), color="negative", position="top")
            logging.exception(f"Error importing habits: {e}")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return