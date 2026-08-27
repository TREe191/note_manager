"""Business operations for creating and managing notes."""

from datetime import datetime, timezone
from typing import Any, Iterable

from .models import Note
from .storage import NoteStorage


class NoteService:
    """Coordinate note creation with the configured storage."""

    def __init__(self, storage: NoteStorage) -> None:
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

    def update_note(
        self, note_number: int, title: str, content: str, tags: Iterable[str]
    ) -> dict[str, Any] | None:
        """Update one note and persist its changed data."""
        notes = self.list_notes()
        if note_number < 1 or note_number > len(notes):
            return None

        note = notes[note_number - 1]
        note["title"] = Note.clean_title(title)
        note["content"] = content.strip()
        note["tags"] = Note.clean_tags(tags)
        note["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.storage.save_notes(notes)
        return note

    def delete_note(self, note_number: int) -> dict[str, Any] | None:
        """Delete one note by its one-based number and persist the change."""
        notes = self.list_notes()
        if note_number < 1 or note_number > len(notes):
            return None

        deleted_note = notes.pop(note_number - 1)
        self.storage.save_notes(notes)
        return deleted_note

    def search_notes(self, keyword: str) -> list[dict[str, Any]]:
        """Find notes by keyword and rank tag matches before text matches."""
        normalized_keyword = keyword.strip().casefold()
        if not normalized_keyword:
            return []

        scored_notes: list[tuple[tuple[int, int], str, dict[str, Any]]] = []
        for note_number, note in enumerate(self.list_notes(), start=1):
            title = str(note.get("title", "")).casefold()
            content = str(note.get("content", "")).casefold()
            tag_score = self._tag_match_score(
                note.get("tags", []), normalized_keyword
            )
            matches_text = (
                normalized_keyword in title or normalized_keyword in content
            )
            if tag_score == (0, 0) and not matches_text:
                continue

            search_result = dict(note)
            search_result["note_number"] = note_number
            updated_at = str(note.get("updated_at", ""))
            scored_notes.append((tag_score, updated_at, search_result))

        scored_notes.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [note for _, _, note in scored_notes]

    @staticmethod
    def _tag_match_score(tags: Iterable[str], keyword: str) -> tuple[int, int]:
        """Score tags by match type and their count of keyword characters."""
        best_score = (0, 0)
        for tag in tags:
            normalized_tag = tag.casefold()
            if normalized_tag == keyword:
                match_type = 2
            elif keyword in normalized_tag:
                match_type = 1
            else:
                continue

            shared_character_count = sum(
                character in keyword for character in normalized_tag
            )
            best_score = max(best_score, (match_type, shared_character_count))

        return best_score
