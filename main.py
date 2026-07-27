"""Personal note manager command-line entry point."""

from pathlib import Path

from src.cli import NoteCli
from src.note_service import NoteService
from src.storage import JsonNoteStorage


def main() -> None:
    """Configure application dependencies and start the command-line program."""
    data_file = Path(__file__).parent / "data" / "notes.json"
    storage = JsonNoteStorage(data_file)
    note_service = NoteService(storage)
    cli = NoteCli(note_service)
    cli.run()


if __name__ == "__main__":
    main()
