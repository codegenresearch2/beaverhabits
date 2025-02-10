import json
from nicegui import events, ui
from beaverhabits.app.db import User
from beaverhabits.frontend.components import menu_header
from beaverhabits.storage.dict import DictHabitList
from beaverhabits.storage.meta import get_root_path
from beaverhabits.storage.storage import HabitList
from beaverhabits.storage import user_storage as user_storage_module
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def import_from_json(text: str) -> HabitList:
    try:
        d = json.loads(text)
        habit_list = DictHabitList(d)
        if not habit_list.habits:
            raise ValueError("No habits found")
        return habit_list
    except json.JSONDecodeError:
        logging.error("Import failed: Invalid JSON")
        raise
    except ValueError as e:
        logging.error(f"Import failed: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

async def import_ui_page(user: User):
    async def handle_upload(e: events.UploadEventArguments):
        try:
            result = await dialog
            if result != "Yes":
                return

            text = e.content.read().decode("utf-8")
            to_habit_list = await import_from_json(text)
            existing_habit_list = await user_storage_module.get_user_habit_list(user)

            if existing_habit_list:
                added, merged, unchanged = existing_habit_list.merge_and_categorize(to_habit_list)
                await user_storage_module.save_user_habit_list(user, merged)
                logging.info(f"Imported {len(to_habit_list.habits)} habits, added {len(added)}, merged {len(merged)}, unchanged {len(unchanged)}.")
            else:
                await user_storage_module.save_user_habit_list(user, to_habit_list)
                logging.info(f"Imported {len(to_habit_list.habits)} new habits.")

            message = f"Imported {len(to_habit_list.habits)} habits"
            if added:
                message += f", added {len(added)} new habits"
            if merged:
                message += f", merged {len(merged)} habits"
            if unchanged:
                message += f", {len(unchanged)} habits unchanged"

            ui.notify(message, position="top", color="positive")
        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as error:
            logging.exception("Import failed")
            ui.notify(str(error), color="negative", position="top")

    with ui.dialog() as dialog, ui.card().classes("w-64"):
        ui.label("Are you sure? All your current habits will be replaced.")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return