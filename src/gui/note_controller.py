"""Adapter between the GUI and the existing note service."""

from typing import Any

from ..note_service import NoteService


class NoteController:
    """Read note data for the GUI while keeping selection stable by ID."""

    def __init__(self, note_service: NoteService) -> None:
        self.note_service = note_service

    def list_notes(self) -> list[dict[str, Any]]:
        """Return the current notes for the left-side list."""
        return self.note_service.list_notes()

    def get_note_detail_by_id(self, note_id: str) -> dict[str, Any] | None:
        """Resolve a stable note ID to the current service-layer number."""
        note_number = self._find_note_number(note_id)
        if note_number is None:
            return None
        return self.note_service.get_note_detail(note_number)

    def _find_note_number(self, note_id: str) -> int | None:
        """Find the current one-based note number for a saved note ID."""
        for note_number, note in enumerate(self.note_service.list_notes(), start=1):
            if note.get("id") == note_id:
                return note_number
        return None
