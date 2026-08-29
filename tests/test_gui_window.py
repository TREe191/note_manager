"""Tests for GUI browse and editor state transitions."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from src.gui.main_window import NoteMainWindow
from src.gui.note_controller import NoteController
from src.note_service import NoteService
from src.storage import JsonNoteStorage


class NoteMainWindowTestCase(unittest.TestCase):
    """Verify the main new-note and in-place editing states."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        data_file = Path(self.temporary_directory.name) / "notes.json"
        self.service = NoteService(JsonNoteStorage(data_file))
        self.first_note = self.service.create_note("第一条", "正文一", ["学习"])
        self.service.create_note("第二条", "正文二", ["Python"])
        self.window = NoteMainWindow(NoteController(self.service))
        self.window.show()
        self.application.processEvents()
        for index in range(self.window.note_list.count()):
            item = self.window.note_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == self.first_note.id:
                self.window.note_list.setCurrentItem(item)
                break
        self.application.processEvents()

    def tearDown(self) -> None:
        self.window.close()
        self.temporary_directory.cleanup()

    def test_new_note_save_refreshes_list_and_selects_new_note(self) -> None:
        """Saving a new note refreshes the list and opens its detail page."""
        self.window._start_new_note()
        self.window.editor_title.setText("新建 GUI 笔记")
        self.window.editor_body.setPlainText("通过图形界面创建。")
        self.window.editor_tags.setText("GUI, PySide6")

        self.window._save_editor()
        self.application.processEvents()

        selected_note = self.service.get_note_detail(3)
        self.assertEqual(self.window.note_list.count(), 3)
        self.assertEqual(self.window.selected_note_id, selected_note["id"])
        self.assertEqual(self.window.detail_title.text(), "新建 GUI 笔记")
        self.assertIs(self.window.right_stack.currentWidget(), self.window.detail_page)

    def test_cancel_existing_edit_restores_the_detail_without_saving(self) -> None:
        """Cancelling an existing draft returns to its original read-only detail."""
        self.window._start_edit_selected_note()
        self.window.editor_title.setText("未保存标题")

        with patch(
            "src.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Discard,
        ):
            self.window._cancel_editor()

        saved_note = self.service.get_note_detail(1)
        self.assertEqual(saved_note["title"], "第一条")
        self.assertEqual(self.window.detail_title.text(), "第一条")
        self.assertIs(self.window.right_stack.currentWidget(), self.window.detail_page)

    def test_existing_edit_save_refreshes_the_selected_detail(self) -> None:
        """Saving an existing draft keeps selection and displays updated values."""
        self.window._start_edit_selected_note()
        self.window.editor_title.setText("更新后的第一条")
        self.window.editor_body.setPlainText("更新后的正文")
        self.window.editor_tags.setText("GUI, 更新")

        self.window._save_editor()
        self.application.processEvents()

        saved_note = self.service.get_note_detail(1)
        self.assertEqual(self.window.selected_note_id, self.first_note.id)
        self.assertEqual(saved_note["title"], "更新后的第一条")
        self.assertEqual(self.window.detail_title.text(), "更新后的第一条")
        self.assertIs(self.window.right_stack.currentWidget(), self.window.detail_page)

    def test_unsaved_draft_can_block_list_selection_change(self) -> None:
        """Keeping a draft restores the previous list selection and editor page."""
        self.window._start_edit_selected_note()
        self.window.editor_body.setPlainText("未保存正文")

        with patch(
            "src.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            self.window.note_list.setCurrentRow(1)
            self.application.processEvents()

        self.assertEqual(self.window.selected_note_id, self.first_note.id)
        self.assertIs(self.window.right_stack.currentWidget(), self.window.editor_page)

    def test_unsaved_draft_can_block_starting_a_new_note(self) -> None:
        """Keeping a draft prevents the new-note action from replacing it."""
        self.window._start_edit_selected_note()
        self.window.editor_body.setPlainText("未保存正文")

        with patch(
            "src.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            self.window._start_new_note()

        self.assertEqual(self.window.editor_title.text(), "第一条")
        self.assertEqual(self.window.editor_body.toPlainText(), "未保存正文")
        self.assertIs(self.window.right_stack.currentWidget(), self.window.editor_page)

    def test_search_filters_list_and_clearing_search_restores_all_notes(self) -> None:
        """Search results use the existing service and clear back to all notes."""
        self.window.search_input.setText("python")
        self.application.processEvents()

        self.assertEqual(self.window.note_list.count(), 1)
        result = self.window.note_list.item(0)
        self.assertEqual(
            result.data(Qt.ItemDataRole.UserRole),
            self.service.get_note_detail(2)["id"],
        )

        self.window.search_input.clear()
        self.application.processEvents()

        self.assertEqual(self.window.note_list.count(), 2)

    def test_sorting_search_results_changes_only_the_visible_order(self) -> None:
        """Sorting results keeps the search filter and saved order unchanged."""
        third_note = self.service.create_note("第三条", "正文三", ["Python"])
        saved_notes = self.service.list_notes()
        saved_notes[0].update(
            {
                "title": "Beta",
                "tags": ["Python"],
                "created_at": "2026-08-27T10:00:00+00:00",
                "updated_at": "2026-08-27T11:00:00+00:00",
            }
        )
        saved_notes[1].update(
            {
                "title": "Alpha",
                "created_at": "2026-08-27T12:00:00+00:00",
                "updated_at": "2026-08-27T13:00:00+00:00",
            }
        )
        saved_notes[2].update(
            {
                "title": "Gamma",
                "created_at": "2026-08-27T14:00:00+00:00",
                "updated_at": "2026-08-27T15:00:00+00:00",
            }
        )
        self.service.storage.save_notes(saved_notes)
        self.window.refresh_notes()

        self.window.search_input.setText("Python")
        self.window.sort_selector.setCurrentIndex(
            self.window.sort_selector.findData("updated_at")
        )
        self.application.processEvents()

        visible_ids = [
            self.window.note_list.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(self.window.note_list.count())
        ]
        self.assertEqual(
            visible_ids,
            [third_note.id, saved_notes[1]["id"], self.first_note.id],
        )
        self.assertEqual(
            [note["id"] for note in self.service.list_notes()],
            [self.first_note.id, saved_notes[1]["id"], third_note.id],
        )

    def test_sorting_keeps_the_current_note_selected(self) -> None:
        """Changing display order preserves the selection by stable ID."""
        self.window.sort_selector.setCurrentIndex(
            self.window.sort_selector.findData("title")
        )
        self.application.processEvents()

        self.assertEqual(self.window.selected_note_id, self.first_note.id)
        self.assertEqual(
            self.window.note_list.currentItem().data(Qt.ItemDataRole.UserRole),
            self.first_note.id,
        )

    def test_confirmed_delete_refreshes_list_and_clears_detail(self) -> None:
        """Confirmed deletion removes the selection and returns to the empty state."""
        with patch(
            "src.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            self.window._delete_selected_note()

        self.assertEqual(self.window.note_list.count(), 1)
        self.assertIsNone(self.window.selected_note_id)
        self.assertIs(self.window.right_stack.currentWidget(), self.window.empty_page)

    def test_cancelled_delete_keeps_the_note_and_detail(self) -> None:
        """Cancelling deletion leaves the selected note and its detail intact."""
        with patch(
            "src.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            self.window._delete_selected_note()

        self.assertEqual(self.window.note_list.count(), 2)
        self.assertEqual(self.window.selected_note_id, self.first_note.id)
        self.assertEqual(self.window.detail_title.text(), "第一条")
