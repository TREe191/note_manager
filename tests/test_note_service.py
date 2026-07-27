"""Tests for note business operations."""

import json
import tempfile
import unittest
from pathlib import Path

from src.note_service import NoteService
from src.storage import JsonNoteStorage


class NoteServiceTestCase(unittest.TestCase):
    """Verify note creation and list retrieval through the service layer."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temporary_directory.name) / "notes.json"
        self.storage = JsonNoteStorage(self.data_file)
        self.service = NoteService(self.storage)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_create_note_saves_note_to_json_file(self) -> None:
        """Creating a note returns it and persists its data."""
        note = self.service.create_note(
            title="Python 学习计划",
            content="完成 unittest 基础测试。",
            tags=["Python", "测试"],
        )

        saved_notes = json.loads(self.data_file.read_text(encoding="utf-8"))

        self.assertEqual(note.title, "Python 学习计划")
        self.assertTrue(note.id)
        self.assertEqual(len(saved_notes), 1)
        self.assertEqual(saved_notes[0]["id"], note.id)
        self.assertEqual(saved_notes[0]["tags"], ["Python", "测试"])

    def test_list_notes_returns_saved_notes(self) -> None:
        """Listing notes returns the records previously created."""
        first_note = self.service.create_note("第一条", "正文一")
        second_note = self.service.create_note("第二条", "正文二", ["学习"])

        notes = self.service.list_notes()

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["id"], first_note.id)
        self.assertEqual(notes[1]["id"], second_note.id)
        self.assertEqual(notes[1]["title"], "第二条")

    def test_get_note_detail_returns_note_for_valid_number(self) -> None:
        """A valid one-based number returns the corresponding saved note."""
        self.service.create_note("第一条", "正文一")
        second_note = self.service.create_note("第二条", "正文二", ["学习"])

        note = self.service.get_note_detail(2)

        self.assertIsNotNone(note)
        self.assertEqual(note["id"], second_note.id)
        self.assertEqual(note["content"], "正文二")
        self.assertEqual(note["tags"], ["学习"])

    def test_get_note_detail_returns_none_for_invalid_number(self) -> None:
        """An unavailable number does not return a note."""
        self.service.create_note("第一条", "正文一")

        self.assertIsNone(self.service.get_note_detail(0))
        self.assertIsNone(self.service.get_note_detail(2))
