"""Tests for SQLite note storage."""

import tempfile
import unittest
from pathlib import Path

from src.note_service import NoteService
from src.sqlite_storage import SqliteNoteStorage


class SqliteNoteStorageTestCase(unittest.TestCase):
    """Verify SQLite persistence matches the current JSON storage contract."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temporary_directory.name) / "notes.db"
        self.storage = SqliteNoteStorage(self.data_file)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_load_notes_returns_empty_list_for_a_new_database(self) -> None:
        """A new database behaves like an empty notebook."""
        self.assertEqual(self.storage.load_notes(), [])
        self.assertTrue(self.data_file.exists())

    def test_save_notes_and_load_notes_preserves_all_fields_and_order(self) -> None:
        """SQLite round-trips IDs, content, tags, timestamps, and list order."""
        notes = [
            {
                "id": "note-2",
                "title": "第二条笔记",
                "content": "包含中文和 Python。",
                "tags": ["学习", "Python"],
                "created_at": "2026-08-27T10:00:00+00:00",
                "updated_at": "2026-08-27T10:30:00+00:00",
                "is_archived": False,
            },
            {
                "id": "note-1",
                "title": "第一条笔记",
                "content": "第二条数据。",
                "tags": [],
                "created_at": "2026-08-27T11:00:00+00:00",
                "updated_at": "2026-08-27T11:30:00+00:00",
                "is_archived": True,
            },
        ]

        self.storage.save_notes(notes)

        self.assertEqual(self.storage.load_notes(), notes)

    def test_save_notes_replaces_previous_records(self) -> None:
        """Saving the current list removes records no longer present."""
        first_notes = [
            {
                "id": "note-1",
                "title": "第一条",
                "content": "正文一",
                "tags": [],
                "created_at": "2026-08-27T00:00:00+00:00",
                "updated_at": "2026-08-27T00:00:00+00:00",
                "is_archived": False,
            },
            {
                "id": "note-2",
                "title": "第二条",
                "content": "正文二",
                "tags": ["测试"],
                "created_at": "2026-08-27T00:00:00+00:00",
                "updated_at": "2026-08-27T00:00:00+00:00",
                "is_archived": False,
            },
        ]

        self.storage.save_notes(first_notes)
        self.storage.save_notes([first_notes[1]])

        self.assertEqual(self.storage.load_notes(), [first_notes[1]])

    def test_note_service_works_with_sqlite_storage(self) -> None:
        """The existing service can create and update notes through SQLite."""
        service = NoteService(self.storage)

        created_note = service.create_note("SQLite 笔记", "初始正文", ["数据库"])
        updated_note = service.update_note(
            1, "更新后的笔记", "更新后的正文", ["SQLite", "测试"]
        )

        self.assertEqual(updated_note["id"], created_note.id)
        self.assertEqual(service.list_notes()[0]["title"], "更新后的笔记")
        self.assertEqual(service.list_notes()[0]["tags"], ["SQLite", "测试"])
