"""Desktop GUI entry point for the personal note manager."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.gui.main_window import NoteMainWindow
from src.gui.note_controller import NoteController
from src.gui.styles import DARK_STYLESHEET
from src.migration import migrate_json_to_sqlite_if_needed
from src.note_service import NoteService
from src.sqlite_storage import SqliteNoteStorage


def main() -> int:
    """Configure dependencies and start the desktop application."""
    data_directory = Path(__file__).parent / "data"
    json_file = data_directory / "notes.json"
    sqlite_file = data_directory / "notes.db"
    migrate_json_to_sqlite_if_needed(json_file, sqlite_file)
    note_service = NoteService(SqliteNoteStorage(sqlite_file))
    controller = NoteController(note_service)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)

    window = NoteMainWindow(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
