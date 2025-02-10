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

async def import_from_json(text: str) -> HabitList:
    try:
        d = json.loads(text)
        habit_list = DictHabitList(d)
        if not habit_list.habits:
            raise ValueError("No habits found")
        return habit_list
    except json.JSONDecodeError:
        logging.exception("Invalid JSON")
        raise ValueError("Invalid JSON")
    except Exception as e:
        logging.exception(f"Error importing habits: {e}")
        raise ValueError(f"Error importing habits: {e}")

async def import_ui_page(user: User):
    async with ui.dialog() as dialog:
        with ui.card().classes("w-64"):
            ui.label("Are you sure? All your current habits will be replaced.")
            with ui.row():
                ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                ui.button("No", on_click=lambda: dialog.submit("No"))

    async def handle_upload(e: events.UploadEventArguments):
        result = await dialog
        if result != "Yes":
            return

        try:
            text = e.content.read().decode("utf-8")
            to_habit_list = await import_from_json(text)
            existing_habit_list = await user_storage.get_user_habit_list(user)

            if existing_habit_list is None:
                await user_storage.save_user_habit_list(user, to_habit_list)
                logging.info(f"Imported {len(to_habit_list.habits)} new habits")
            else:
                existing_habit_ids = {habit.id for habit in existing_habit_list.habits}
                to_habit_ids = {habit.id for habit in to_habit_list.habits}
                
                added_habits = [habit for habit in to_habit_list.habits if habit.id not in existing_habit_ids]
                merged_habits = [habit for habit in to_habit_list.habits if habit.id in existing_habit_ids]
                unchanged_habits = [habit for habit in existing_habit_list.habits if habit.id in to_habit_ids]

                merged_habit_list = existing_habit_list.merge(to_habit_list)
                await user_storage.save_user_habit_list(user, merged_habit_list)

                logging.info(f"Imported {len(added_habits)} new habits and {len(merged_habits)} merged habits")

            ui.notify(
                f"Imported {len(to_habit_list.habits)} habits",
                position="top",
                color="positive",
            )
        except ValueError as e:
            ui.notify(str(e), color="negative", position="top")
        except json.JSONDecodeError:
            ui.notify("Import failed: Invalid JSON", color="negative", position="top")
        except Exception as e:
            ui.notify("An error occurred. Please try again later.", color="negative", position="top")
            logging.exception(f"Error importing habits: {e}")

    menu_header("Import", target=get_root_path())

    # Upload: https://nicegui.io/documentation/upload
    ui.upload(on_upload=handle_upload, max_files=1).props("accept=.json")
    return