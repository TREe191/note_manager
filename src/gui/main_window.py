"""Main PySide6 window for browsing saved notes."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .note_controller import NoteController


class NoteMainWindow(QMainWindow):
    """Show saved notes in a two-pane desktop layout."""

    def __init__(self, controller: NoteController) -> None:
        super().__init__()
        self.controller = controller
        self.selected_note_id: str | None = None

        self.setWindowTitle("Personal Note Manager")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        self._build_interface()
        self.refresh_notes()

    def _build_interface(self) -> None:
        """Build the header, note list, and detail panels."""
        central_widget = QWidget()
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 16, 18, 18)
        root_layout.setSpacing(14)
        root_layout.addLayout(self._create_header())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._create_note_list_panel())
        splitter.addWidget(self._create_detail_panel())
        splitter.setSizes([330, 850])
        root_layout.addWidget(splitter, 1)

        self.setCentralWidget(central_widget)

    def _create_header(self) -> QHBoxLayout:
        """Create placeholders for the upcoming search and creation actions."""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索功能将在后续阶段启用")
        self.search_input.setEnabled(False)

        self.new_note_button = QPushButton("+ 新建笔记")
        self.new_note_button.setEnabled(False)

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

    def _create_detail_panel(self) -> QStackedWidget:
        """Create empty and detail states for the right-side panel."""
        self.detail_stack = QStackedWidget()
        self.empty_page = self._create_empty_page()
        self.detail_page = self._create_detail_page()
        self.detail_stack.addWidget(self.empty_page)
        self.detail_stack.addWidget(self.detail_page)
        return self.detail_stack

    def _create_empty_page(self) -> QWidget:
        """Create the message displayed when no note is selected."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        title = QLabel("选择一条笔记")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("从左侧列表选择笔记后，可在这里查看完整内容。")
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

        layout.addWidget(self.detail_title)
        layout.addWidget(self.detail_tags)
        layout.addWidget(self.detail_body, 1)
        layout.addWidget(self.detail_dates)
        return page

    def refresh_notes(self) -> None:
        """Reload the list while preserving selection by stable note ID."""
        notes = self.controller.list_notes()
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
        """Show the detail page for the ID stored in the selected list item."""
        if current is None:
            self.selected_note_id = None
            self._show_empty_state()
            return

        note_id = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(note_id, str):
            self.selected_note_id = None
            self._show_empty_state()
            return

        self.selected_note_id = note_id
        note = self.controller.get_note_detail_by_id(note_id)
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
        self.detail_stack.setCurrentWidget(self.detail_page)

    def _show_empty_state(self) -> None:
        """Switch the detail area back to its empty state."""
        self.detail_stack.setCurrentWidget(self.empty_page)
