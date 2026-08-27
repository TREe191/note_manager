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

    def test_create_note_uses_the_existing_service(self) -> None:
        """The controller creates a note without duplicating business rules."""
        note = self.controller.create_note("新建笔记", "新建正文", ["GUI"])

        saved_note = self.controller.get_note_detail_by_id(note["id"])
        self.assertEqual(saved_note["title"], "新建笔记")
        self.assertEqual(saved_note["tags"], ["GUI"])

    def test_update_note_by_id_updates_the_matching_note(self) -> None:
        """The controller resolves a stable ID before updating through the service."""
        updated_note = self.controller.update_note_by_id(
            self.second_note.id,
            "更新后的第二条",
            "更新后的正文",
            ["GUI", "更新"],
        )

        self.assertIsNotNone(updated_note)
        self.assertEqual(updated_note["title"], "更新后的第二条")
        self.assertEqual(
            self.controller.get_note_detail_by_id(self.second_note.id)["content"],
            "更新后的正文",
        )

    def test_search_notes_uses_the_existing_service_ranking(self) -> None:
        """The controller exposes the service-layer search results unchanged."""
        results = self.controller.search_notes("学习")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.second_note.id)
        self.assertEqual(results[0]["note_number"], 2)

    def test_delete_note_by_id_removes_the_matching_note(self) -> None:
        """The controller resolves a stable ID before deleting through the service."""
        deleted_note = self.controller.delete_note_by_id(self.second_note.id)

        self.assertEqual(deleted_note["id"], self.second_note.id)
        self.assertIsNone(
            self.controller.get_note_detail_by_id(self.second_note.id)
        )
