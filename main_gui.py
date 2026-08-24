"""Desktop GUI entry point for the personal note manager."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.gui.main_window import NoteMainWindow
from src.gui.note_controller import NoteController
from src.gui.styles import DARK_STYLESHEET
from src.note_service import NoteService
from src.storage import JsonNoteStorage


def main() -> int:
    """Configure dependencies and start the desktop application."""
    data_file = Path(__file__).parent / "data" / "notes.json"
    note_service = NoteService(JsonNoteStorage(data_file))
    controller = NoteController(note_service)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)

    window = NoteMainWindow(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
