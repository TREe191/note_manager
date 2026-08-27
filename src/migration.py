"""One-time migration helpers for note data."""

from pathlib import Path

from .sqlite_storage import SqliteNoteStorage
from .storage import JsonNoteStorage


def migrate_json_to_sqlite_if_needed(
    json_file: str | Path, sqlite_file: str | Path
) -> bool:
    """Copy JSON notes into a new SQLite database once.

    Return whether a migration was performed. The source JSON file is never
    changed, and an existing SQLite file prevents a second import.
    """
    json_path = Path(json_file)
    sqlite_path = Path(sqlite_file)
    if sqlite_path.exists() or not json_path.exists():
        return False

    notes = JsonNoteStorage(json_path).load_notes()
    SqliteNoteStorage(sqlite_path).save_notes(notes)
    return True
