"""Tests for JSON note storage."""

import tempfile
import unittest
from pathlib import Path

from src.storage import JsonNoteStorage


class JsonNoteStorageTestCase(unittest.TestCase):
    """Verify JSON persistence behavior without using real note data."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temporary_directory.name) / "notes.json"
        self.storage = JsonNoteStorage(self.data_file)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_load_notes_returns_empty_list_when_file_is_missing(self) -> None:
        """A new storage location behaves like an empty notebook."""
        self.assertEqual(self.storage.load_notes(), [])

    def test_save_notes_and_load_notes_round_trip(self) -> None:
        """Saved JSON records can be loaded back without changes."""
        notes = [
            {
                "id": "note-1",
                "title": "测试笔记",
                "content": "测试 JSON 保存和读取。",
                "tags": ["测试"],
                "created_at": "2026-07-27T00:00:00+00:00",
                "updated_at": "2026-07-27T00:00:00+00:00",
                "is_archived": False,
            }
        ]

        self.storage.save_notes(notes)

        self.assertTrue(self.data_file.exists())
        self.assertEqual(self.storage.load_notes(), notes)
