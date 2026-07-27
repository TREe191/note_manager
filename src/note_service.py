"""Business operations for creating and managing notes."""

from typing import Any, Iterable

from .models import Note
from .storage import JsonNoteStorage


class NoteService:
    """Coordinate note creation with the configured storage."""

    def __init__(self, storage: JsonNoteStorage) -> None:
        self.storage = storage

    def create_note(
        self, title: str, content: str, tags: Iterable[str] | None = None
    ) -> Note:
        """Create a note and save it to the JSON data file."""
        note = Note.create(title=title, content=content, tags=tags)
        notes = self.storage.load_notes()
        notes.append(note.to_dict())
        self.storage.save_notes(notes)
        return note

    def list_notes(self) -> list[dict[str, Any]]:
        """Return all saved notes for display."""
        return self.storage.load_notes()

    def get_note_detail(self, note_number: int) -> dict[str, Any] | None:
        """Return one note by its one-based number in the note list."""
        notes = self.list_notes()
        if note_number < 1 or note_number > len(notes):
            return None
        return notes[note_number - 1]
