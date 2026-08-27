"""Personal note manager command-line entry point."""

from pathlib import Path

from src.cli import NoteCli
from src.migration import migrate_json_to_sqlite_if_needed
from src.note_service import NoteService
from src.sqlite_storage import SqliteNoteStorage


def main() -> None:
    """Configure application dependencies and start the command-line program."""
    data_directory = Path(__file__).parent / "data"
    json_file = data_directory / "notes.json"
    sqlite_file = data_directory / "notes.db"
    migrate_json_to_sqlite_if_needed(json_file, sqlite_file)
    storage = SqliteNoteStorage(sqlite_file)
    note_service = NoteService(storage)
    cli = NoteCli(note_service)
    cli.run()


if __name__ == "__main__":
    main()
