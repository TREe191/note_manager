"""Tests for the GUI controller adapter."""

import tempfile
import unittest
from pathlib import Path

from src.gui.note_controller import NoteController
from src.note_service import NoteService
from src.storage import JsonNoteStorage


class NoteControllerTestCase(unittest.TestCase):
    """Verify that GUI selection uses stable note IDs."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        data_file = Path(self.temporary_directory.name) / "notes.json"
        service = NoteService(JsonNoteStorage(data_file))
        self.controller = NoteController(service)
        service.create_note("第一条", "正文一")
        self.second_note = service.create_note("第二条", "正文二", ["学习"])

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_get_note_detail_by_id_returns_the_matching_note(self) -> None:
        """The controller resolves a stable ID through the existing service."""
        note = self.controller.get_note_detail_by_id(self.second_note.id)

        self.assertIsNotNone(note)
        self.assertEqual(note["title"], "第二条")
        self.assertEqual(note["content"], "正文二")

    def test_get_note_detail_by_id_returns_none_for_unknown_id(self) -> None:
        """An unknown stable ID does not return a note."""
        self.assertIsNone(self.controller.get_note_detail_by_id("missing-id"))
