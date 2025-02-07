from beaverhabits.configs import StorageType, settings\\\nfrom beaverhabits.storage.session_file import SessionDictStorage, SessionStorage\\\\nfrom beaverhabits.storage.storage import UserStorage\\\\nfrom beaverhabits.storage.user_db import UserDatabaseStorage\\\\nfrom beaverhabits.storage.user_file import UserDiskStorage\\\\n\n\nsession_storage = SessionDictStorage()\\\\nuser_disk_storage = UserDiskStorage()\\\\nuser_database_storage = UserDatabaseStorage()\\\\nsqlite_storage = None\\\\n\n\ndef get_sessions_storage() -> SessionStorage:\\\\n    return session_storage\\\\n\n\ndef get_user_dict_storage() -> UserStorage:\\\\n    if settings.HABITS_STORAGE == StorageType.USER_DISK:\\\\n        return user_disk_storage\\\\n    if settings.HABITS_STORAGE == StorageType.USER_DATABASE:\\\\n        return user_database_storage\\\\n    raise NotImplementedError("Storage type not implemented")