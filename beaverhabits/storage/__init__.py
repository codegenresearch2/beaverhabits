from beaverhabits.configs import StorageType, settings
from beaverhabits.storage.session_file import SessionDictStorage, SessionStorage
from beaverhabits.storage.user_db import UserDatabaseStorage
from beaverhabits.storage.user_file import UserDiskStorage


def get_user_storage():
    if settings.HABITS_STORAGE == StorageType.USER_DISK:
        return UserDiskStorage()
    elif settings.HABITS_STORAGE == StorageType.USER_DATABASE:
        return UserDatabaseStorage()
    raise NotImplementedError('Storage type not implemented')