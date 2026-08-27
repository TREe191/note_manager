"""Tests for one-time JSON to SQLite note migration."""

import tempfile
import unittest
from pathlib import Path

from src.migration import migrate_json_to_sqlite_if_needed
from src.sqlite_storage import SqliteNoteStorage
from src.storage import JsonNoteStorage


class JsonToSqliteMigrationTestCase(unittest.TestCase):
    """Verify application data moves once without changing its JSON backup."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_directory = Path(self.temporary_directory.name)
        self.json_file = self.data_directory / "notes.json"
        self.sqlite_file = self.data_directory / "notes.db"
        self.notes = [
            {
                "id": "note-1",
                "title": "已有笔记",
                "content": "迁移测试正文。",
                "tags": ["迁移", "SQLite"],
                "created_at": "2026-08-27T00:00:00+00:00",
                "updated_at": "2026-08-27T01:00:00+00:00",
                "is_archived": False,
            }
        ]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_migration_copies_json_notes_and_preserves_the_source_file(self) -> None:
        """A missing database is populated from the existing JSON note list."""
        JsonNoteStorage(self.json_file).save_notes(self.notes)
        original_json = self.json_file.read_text(encoding="utf-8")

        migrated = migrate_json_to_sqlite_if_needed(
            self.json_file, self.sqlite_file
        )

        self.assertTrue(migrated)
        self.assertEqual(SqliteNoteStorage(self.sqlite_file).load_notes(), self.notes)
        self.assertEqual(self.json_file.read_text(encoding="utf-8"), original_json)

    def test_migration_is_skipped_when_sqlite_database_already_exists(self) -> None:
        """An existing database prevents a second import from JSON."""
        JsonNoteStorage(self.json_file).save_notes(self.notes)
        existing_notes = [dict(self.notes[0], id="sqlite-note", title="SQLite 数据")]
        SqliteNoteStorage(self.sqlite_file).save_notes(existing_notes)

        migrated = migrate_json_to_sqlite_if_needed(
            self.json_file, self.sqlite_file
        )

        self.assertFalse(migrated)
        self.assertEqual(
            SqliteNoteStorage(self.sqlite_file).load_notes(), existing_notes
        )

    def test_migration_is_skipped_when_json_file_is_missing(self) -> None:
        """A new installation starts with an empty SQLite database on first use."""
        migrated = migrate_json_to_sqlite_if_needed(
            self.json_file, self.sqlite_file
        )

        self.assertFalse(migrated)
        self.assertFalse(self.sqlite_file.exists())
