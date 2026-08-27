"""Main PySide6 window for browsing and editing saved notes."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .note_controller import NoteController


class NoteMainWindow(QMainWindow):
    """Show notes and manage an in-place editor in a two-pane layout."""

    def __init__(self, controller: NoteController) -> None:
        super().__init__()
        self.controller = controller
        self.selected_note_id: str | None = None
        self.editing_note_id: str | None = None
        self.editor_initial_values: tuple[str, str, str] | None = None

        self.setWindowTitle("Personal Note Manager")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        self._build_interface()
        self.refresh_notes()

    def _build_interface(self) -> None:
        """Build the header, note list, and right-side pages."""
        central_widget = QWidget()
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 16, 18, 18)
        root_layout.setSpacing(14)
        root_layout.addLayout(self._create_header())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._create_note_list_panel())
        splitter.addWidget(self._create_right_panel())
        splitter.setSizes([330, 850])
        root_layout.addWidget(splitter, 1)

        self.setCentralWidget(central_widget)

    def _create_header(self) -> QHBoxLayout:
        """Create the search field and the new-note action."""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索标题、正文或标签")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.refresh_notes)

        self.new_note_button = QPushButton("+ 新建笔记")
        self.new_note_button.clicked.connect(self._start_new_note)

        layout.addWidget(self.search_input, 1)
        layout.addWidget(self.new_note_button)
        return layout

    def _create_note_list_panel(self) -> QWidget:
        """Create the left-side list of saved notes."""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        heading = QLabel("笔记")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        self.note_list = QListWidget()
        self.note_list.setAlternatingRowColors(False)
        self.note_list.setWordWrap(True)
        self.note_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.note_list.currentItemChanged.connect(self._on_note_selected)
        layout.addWidget(self.note_list, 1)
        return panel

    def _create_right_panel(self) -> QStackedWidget:
        """Create empty, detail, and editor states for the right-side panel."""
        self.right_stack = QStackedWidget()
        self.empty_page = self._create_empty_page()
        self.detail_page = self._create_detail_page()
        self.editor_page = self._create_editor_page()
        self.right_stack.addWidget(self.empty_page)
        self.right_stack.addWidget(self.detail_page)
        self.right_stack.addWidget(self.editor_page)
        return self.right_stack

    def _create_empty_page(self) -> QWidget:
        """Create the message displayed when no note is selected."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        title = QLabel("选择一条笔记")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("从左侧列表选择笔记，或新建一条笔记。")
        hint.setObjectName("emptyHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(hint)
        return page

    def _create_detail_page(self) -> QWidget:
        """Create the read-only full note detail view."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 18, 26, 20)
        layout.setSpacing(12)

        self.detail_title = QLabel()
        self.detail_title.setObjectName("noteTitle")
        self.detail_title.setWordWrap(True)

        self.detail_tags = QLabel()
        self.detail_tags.setObjectName("metadata")

        self.detail_body = QPlainTextEdit()
        self.detail_body.setReadOnly(True)
        self.detail_body.setPlaceholderText("这条笔记没有正文。")
        self.detail_body.setMinimumHeight(240)

        self.detail_dates = QLabel()
        self.detail_dates.setObjectName("metadata")
        self.detail_dates.setWordWrap(True)

        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self._start_edit_selected_note)
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self._delete_selected_note)
        actions = QHBoxLayout()
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        layout.addWidget(self.detail_title)
        layout.addWidget(self.detail_tags)
        layout.addWidget(self.detail_body, 1)
        layout.addWidget(self.detail_dates)
        layout.addLayout(actions)
        return page

    def _create_editor_page(self) -> QWidget:
        """Create the shared editor used for both new and existing notes."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 18, 26, 20)
        layout.setSpacing(12)

        self.editor_heading = QLabel()
        self.editor_heading.setObjectName("noteTitle")

        self.editor_title = QLineEdit()
        self.editor_title.setPlaceholderText("标题")

        self.editor_body = QPlainTextEdit()
        self.editor_body.setPlaceholderText("正文")
        self.editor_body.setMinimumHeight(240)

        self.editor_tags = QLineEdit()
        self.editor_tags.setPlaceholderText("标签，使用逗号分隔")

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._save_editor)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._cancel_editor)
        actions = QHBoxLayout()
        actions.addWidget(self.save_button)
        actions.addWidget(self.cancel_button)
        actions.addStretch()

        layout.addWidget(self.editor_heading)
        layout.addWidget(self.editor_title)
        layout.addWidget(self.editor_body, 1)
        layout.addWidget(self.editor_tags)
        layout.addLayout(actions)
        return page

    def refresh_notes(self, _keyword: str | None = None) -> None:
        """Reload the list while preserving selection by stable note ID."""
        notes = self._notes_for_current_filter()
        selected_item: QListWidgetItem | None = None

        self.note_list.blockSignals(True)
        try:
            self.note_list.clear()
            for note in notes:
                item = self._create_note_list_item(note)
                self.note_list.addItem(item)
                if note.get("id") == self.selected_note_id:
                    selected_item = item
        finally:
            self.note_list.blockSignals(False)

        if selected_item is not None:
            self.note_list.setCurrentItem(selected_item)
        elif self._is_editing():
            self.note_list.clearSelection()
        elif self.selected_note_id is not None and self._selected_note_detail():
            self.note_list.clearSelection()
            self._show_selected_note()
        else:
            self.selected_note_id = None
            self._show_empty_state()

    def _create_note_list_item(self, note: dict[str, Any]) -> QListWidgetItem:
        """Build a compact list item and attach the note's stable ID."""
        title = str(note.get("title", "未命名笔记"))
        tags = note.get("tags", [])
        tags_text = ", ".join(tags) if tags else "无标签"
        updated_at = str(note.get("updated_at", "未知"))
        short_updated_at = updated_at.replace("T", " ")[:16]
        item = QListWidgetItem(f"{title}\n{tags_text}  |  {short_updated_at}")
        item.setData(Qt.ItemDataRole.UserRole, note.get("id"))
        item.setToolTip(title)
        return item

    def _on_note_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        """Show a selected note, protecting an unsaved editor draft."""
        if current is None:
            return

        note_id = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(note_id, str):
            self._show_empty_state()
            return

        if self._is_editing() and note_id != self.selected_note_id:
            if not self._confirm_discard_changes():
                self._restore_list_selection()
                return
            self._finish_editing()

        self.selected_note_id = note_id
        self._show_selected_note()

    def _start_new_note(self) -> None:
        """Open a blank editor after confirming any unsaved changes."""
        if not self._confirm_discard_changes():
            return
        self._show_editor(None)

    def _start_edit_selected_note(self) -> None:
        """Open the current selected note in the shared editor."""
        note = self._selected_note_detail()
        if note is None:
            return
        self._show_editor(note)

    def _show_editor(self, note: dict[str, Any] | None) -> None:
        """Populate the editor for a new note or an existing selected note."""
        if note is None:
            self.editing_note_id = None
            title = ""
            content = ""
            tags_text = ""
            self.editor_heading.setText("新建笔记")
        else:
            self.editing_note_id = str(note.get("id", ""))
            title = str(note.get("title", ""))
            content = str(note.get("content", ""))
            tags_text = ", ".join(note.get("tags", []))
            self.editor_heading.setText("编辑笔记")

        self.editor_title.setText(title)
        self.editor_body.setPlainText(content)
        self.editor_tags.setText(tags_text)
        self.editor_initial_values = (title, content, tags_text)
        self.right_stack.setCurrentWidget(self.editor_page)
        self.editor_title.setFocus()

    def _save_editor(self) -> None:
        """Create or update a note through the controller, then refresh the UI."""
        title = self.editor_title.text()
        content = self.editor_body.toPlainText()
        tags_text = self.editor_tags.text()
        tags = tags_text.split(",") if tags_text.strip() else []

        try:
            if self.editing_note_id is None:
                saved_note = self.controller.create_note(title, content, tags)
            else:
                saved_note = self.controller.update_note_by_id(
                    self.editing_note_id, title, content, tags
                )
        except ValueError as error:
            QMessageBox.warning(self, "无法保存笔记", str(error))
            return

        if saved_note is None:
            QMessageBox.warning(self, "无法保存笔记", "未找到要更新的笔记。")
            self._finish_editing()
            self.selected_note_id = None
            self._show_empty_state()
            return

        self.selected_note_id = str(saved_note["id"])
        self._finish_editing()
        self.refresh_notes()

    def _cancel_editor(self) -> None:
        """Discard an editor draft only after user confirmation when needed."""
        if not self._confirm_discard_changes():
            return
        self._finish_editing()
        self._show_selected_note()

    def _selected_note_detail(self) -> dict[str, Any] | None:
        """Return the current selected note detail, or no note when unselected."""
        if self.selected_note_id is None:
            return None
        return self.controller.get_note_detail_by_id(self.selected_note_id)

    def _notes_for_current_filter(self) -> list[dict[str, Any]]:
        """Return all notes or the current service-ranked search results."""
        keyword = self.search_input.text().strip()
        if not keyword:
            return self.controller.list_notes()
        return self.controller.search_notes(keyword)

    def _show_selected_note(self) -> None:
        """Display the current selection, falling back to the empty state."""
        note = self._selected_note_detail()
        if note is None:
            self.selected_note_id = None
            self._show_empty_state()
            return
        self._show_note_detail(note)

    def _show_note_detail(self, note: dict[str, Any]) -> None:
        """Fill the detail view with the currently selected note."""
        tags = note.get("tags", [])
        tags_text = ", ".join(tags) if tags else "无标签"
        created_at = note.get("created_at", "未知")
        updated_at = note.get("updated_at", "未知")

        self.detail_title.setText(str(note.get("title", "未命名笔记")))
        self.detail_tags.setText(f"标签：{tags_text}")
        self.detail_body.setPlainText(str(note.get("content", "")))
        self.detail_dates.setText(
            f"创建时间：{created_at}\n更新时间：{updated_at}"
        )
        self.right_stack.setCurrentWidget(self.detail_page)

    def _show_empty_state(self) -> None:
        """Switch the right-side area back to its empty state."""
        self.right_stack.setCurrentWidget(self.empty_page)

    def _delete_selected_note(self) -> None:
        """Confirm and delete the currently selected note through the controller."""
        note = self._selected_note_detail()
        if note is None or self.selected_note_id is None:
            return

        title = str(note.get("title", "未命名笔记"))
        result = QMessageBox.question(
            self,
            "确认删除笔记",
            f"确定要删除“{title}”吗？此操作无法撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        deleted_note = self.controller.delete_note_by_id(self.selected_note_id)
        if deleted_note is None:
            QMessageBox.warning(self, "无法删除笔记", "未找到要删除的笔记。")
            return

        self.selected_note_id = None
        self.refresh_notes()

    def _is_editing(self) -> bool:
        """Return whether the editor page is currently visible."""
        return self.right_stack.currentWidget() is self.editor_page

    def _has_unsaved_changes(self) -> bool:
        """Compare editor fields with the values originally shown to the user."""
        if not self._is_editing() or self.editor_initial_values is None:
            return False

        current_values = (
            self.editor_title.text(),
            self.editor_body.toPlainText(),
            self.editor_tags.text(),
        )
        return current_values != self.editor_initial_values

    def _confirm_discard_changes(self) -> bool:
        """Ask whether a changed draft may be discarded before navigation."""
        if not self._has_unsaved_changes():
            return True

        result = QMessageBox.question(
            self,
            "放弃未保存修改？",
            "当前笔记有未保存的修改。是否放弃这些修改？",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return result == QMessageBox.StandardButton.Discard

    def _restore_list_selection(self) -> None:
        """Restore the previous list item after the user keeps a draft."""
        self.note_list.blockSignals(True)
        try:
            for index in range(self.note_list.count()):
                item = self.note_list.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == self.selected_note_id:
                    self.note_list.setCurrentItem(item)
                    return
            self.note_list.clearSelection()
        finally:
            self.note_list.blockSignals(False)

    def _finish_editing(self) -> None:
        """Clear temporary editor state after saving or discarding a draft."""
        self.editing_note_id = None
        self.editor_initial_values = None
        self.editor_title.clear()
        self.editor_body.clear()
        self.editor_tags.clear()
