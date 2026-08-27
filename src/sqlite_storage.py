"""SQLite persistence for note records."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class SqliteNoteStorage:
    """Read and write note records in a local SQLite database."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def load_notes(self) -> list[dict[str, Any]]:
        """Return all notes in the same order used by the current service."""
        self._ensure_schema()
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, title, content, tags, created_at, updated_at, is_archived
                FROM notes
                ORDER BY sort_order ASC
                """
            ).fetchall()

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "tags": json.loads(row["tags"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "is_archived": bool(row["is_archived"]),
            }
            for row in rows
        ]

    def save_notes(self, notes: list[dict[str, Any]]) -> None:
        """Replace saved notes in one transaction while preserving their order."""
        self._ensure_schema()
        rows = [
            (
                note["id"],
                note["title"],
                note["content"],
                json.dumps(note.get("tags", []), ensure_ascii=False),
                note["created_at"],
                note["updated_at"],
                int(bool(note.get("is_archived", False))),
                sort_order,
            )
            for sort_order, note in enumerate(notes)
        ]

        with closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM notes")
                connection.executemany(
                    """
                    INSERT INTO notes (
                        id, title, content, tags, created_at, updated_at,
                        is_archived, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )

    def _ensure_schema(self) -> None:
        """Create the notes table when the database is first used."""
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        is_archived INTEGER NOT NULL DEFAULT 0,
                        sort_order INTEGER NOT NULL
                    )
                    """
                )

    def _connect(self) -> sqlite3.Connection:
        """Open a database connection configured for dictionary-style rows."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.file_path)
        connection.row_factory = sqlite3.Row
        return connection
