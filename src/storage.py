"""Persistence interface for reading and writing note data."""

import json
from pathlib import Path
from typing import Any


class JsonNoteStorage:
    """Read and write note records in a local JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load_notes(self) -> list[dict[str, Any]]:
        """Return all saved notes, or an empty list for a new data file."""
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as data_file:
            notes = json.load(data_file)

        if not isinstance(notes, list):
            raise ValueError("The note data file must contain a JSON list.")

        return notes

    def save_notes(self, notes: list[dict[str, Any]]) -> None:
        """Save all note records to the configured JSON file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as data_file:
            json.dump(notes, data_file, ensure_ascii=False, indent=2)
