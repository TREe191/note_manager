"""Tests for note business operations."""

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from src.note_service import NoteService
from src.storage import JsonNoteStorage


class NoteServiceTestCase(unittest.TestCase):
    """Verify note creation, retrieval, and editing through the service layer."""

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

    def test_update_note_changes_fields_time_and_saved_data(self) -> None:
        """Editing a note updates its fields, timestamp, and JSON record."""
        note = self.service.create_note("原始标题", "原始正文", ["原始标签"])
        update_time = datetime(2026, 7, 28, 9, 0, tzinfo=timezone.utc)

        with patch("src.note_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = update_time
            updated_note = self.service.update_note(
                note_number=1,
                title="更新后的标题",
                content="更新后的正文",
                tags=["Python", "测试", "Python"],
            )

        saved_note = self.storage.load_notes()[0]
        self.assertIsNotNone(updated_note)
        self.assertEqual(updated_note["id"], note.id)
        self.assertEqual(updated_note["title"], "更新后的标题")
        self.assertEqual(updated_note["content"], "更新后的正文")
        self.assertEqual(updated_note["tags"], ["Python", "测试"])
        self.assertEqual(updated_note["updated_at"], update_time.isoformat())
        self.assertEqual(saved_note, updated_note)

    def test_update_note_returns_none_for_invalid_number(self) -> None:
        """Editing an unavailable number does not save a note."""
        self.assertIsNone(
            self.service.update_note(1, "标题", "正文", ["标签"])
        )

    def test_delete_note_removes_note_and_saves_remaining_notes(self) -> None:
        """Deleting a valid number removes only the selected note."""
        first_note = self.service.create_note("第一条", "正文一")
        second_note = self.service.create_note("第二条", "正文二")

        deleted_note = self.service.delete_note(1)

        saved_notes = self.storage.load_notes()
        self.assertIsNotNone(deleted_note)
        self.assertEqual(deleted_note["id"], first_note.id)
        self.assertEqual(saved_notes, [second_note.to_dict()])

    def test_delete_note_does_not_save_for_invalid_number(self) -> None:
        """An invalid number leaves the saved notes unchanged."""
        note = self.service.create_note("第一条", "正文一")

        deleted_note = self.service.delete_note(2)

        self.assertIsNone(deleted_note)
        self.assertEqual(self.storage.load_notes(), [note.to_dict()])

    def test_search_notes_ranks_tag_matches_then_updated_time(self) -> None:
        """Search ranks exact tags, tag character scores, then update time."""
        self.storage.save_notes(
            [
                {
                    "id": "1",
                    "title": "Exact tag",
                    "content": "",
                    "tags": ["Python"],
                    "created_at": "2026-07-01T00:00:00+00:00",
                    "updated_at": "2026-07-01T00:00:00+00:00",
                    "is_archived": False,
                },
                {
                    "id": "2",
                    "title": "Repeated tag characters",
                    "content": "",
                    "tags": ["PythonPython"],
                    "created_at": "2026-07-01T00:00:00+00:00",
                    "updated_at": "2026-07-02T00:00:00+00:00",
                    "is_archived": False,
                },
                {
                    "id": "3",
                    "title": "Contained tag",
                    "content": "",
                    "tags": ["Python guide"],
                    "created_at": "2026-07-01T00:00:00+00:00",
                    "updated_at": "2026-07-03T00:00:00+00:00",
                    "is_archived": False,
                },
                {
                    "id": "4",
                    "title": "Python in title",
                    "content": "",
                    "tags": ["other"],
                    "created_at": "2026-07-01T00:00:00+00:00",
                    "updated_at": "2026-07-05T00:00:00+00:00",
                    "is_archived": False,
                },
                {
                    "id": "5",
                    "title": "Body match",
                    "content": "Learn python from examples.",
                    "tags": [],
                    "created_at": "2026-07-01T00:00:00+00:00",
                    "updated_at": "2026-07-04T00:00:00+00:00",
                    "is_archived": False,
                },
            ]
        )

        results = self.service.search_notes("PYTHON")

        self.assertEqual([note["note_number"] for note in results], [1, 2, 3, 4, 5])
        self.assertEqual(results[0]["title"], "Exact tag")
        self.assertEqual(results[-1]["title"], "Body match")

    def test_search_notes_returns_empty_list_for_blank_or_missing_keyword(self) -> None:
        """Blank or unmatched keywords return no search results."""
        self.service.create_note("第一条", "正文一", ["学习"])

        self.assertEqual(self.service.search_notes("   "), [])
        self.assertEqual(self.service.search_notes("不存在"), [])
