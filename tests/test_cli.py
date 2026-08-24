"""Tests for V1.1 command-line navigation."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src.cli import NoteCli
from src.note_service import NoteService
from src.storage import JsonNoteStorage


class NoteCliTestCase(unittest.TestCase):
    """Verify list and search navigation into note details."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        data_file = Path(self.temporary_directory.name) / "notes.json"
        self.service = NoteService(JsonNoteStorage(data_file))
        self.service.create_note("第一条笔记", "第一条正文", ["学习"])
        self.service.create_note("Python 笔记", "Python 正文", ["Python"])
        self.cli = NoteCli(self.service)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_list_number_opens_matching_detail_and_zero_returns(self) -> None:
        """A list number opens its detail, then zero returns through both pages."""
        output = self._run_cli("2", "2", "0", "0", "0")

        self.assertIn("标题：Python 笔记", output)
        self.assertIn("正文：Python 正文", output)
        self.assertIn("已退出程序。", output)

    def test_search_result_number_opens_matching_detail_and_zero_returns(self) -> None:
        """A displayed original search number opens the matching detail."""
        output = self._run_cli("6", "python", "2", "0", "0", "0")

        self.assertIn("2. Python 笔记", output)
        self.assertIn("标题：Python 笔记", output)
        self.assertIn("已退出程序。", output)

    def test_invalid_list_number_shows_message_and_allows_retry(self) -> None:
        """An invalid list number leaves the selection page usable."""
        output = self._run_cli("2", "99", "1", "0", "0", "0")

        self.assertIn("未找到该编号的笔记。", output)
        self.assertIn("标题：第一条笔记", output)
        self.assertIn("已退出程序。", output)

    def test_invalid_search_number_shows_message_and_allows_retry(self) -> None:
        """A number outside the results can be corrected without leaving search."""
        output = self._run_cli("6", "python", "1", "2", "0", "0", "0")

        self.assertIn("该编号不在当前搜索结果中。", output)
        self.assertIn("标题：Python 笔记", output)
        self.assertIn("已退出程序。", output)

    def test_detail_edit_refreshes_the_current_note(self) -> None:
        """Editing in detail saves changes and displays the updated note again."""
        output = self._run_cli(
            "2",
            "1",
            "1",
            "更新后的标题",
            "更新后的正文",
            "更新, 标签",
            "0",
            "0",
            "0",
        )

        note = self.service.get_note_detail(1)
        self.assertEqual(note["title"], "更新后的标题")
        self.assertEqual(note["content"], "更新后的正文")
        self.assertEqual(note["tags"], ["更新", "标签"])
        self.assertIn("笔记已更新。", output)
        self.assertIn("标题：更新后的标题", output)

    def test_detail_delete_returns_to_previous_page_after_confirmation(self) -> None:
        """Confirmed deletion closes detail and returns to the search results."""
        output = self._run_cli("6", "python", "2", "2", "y", "0", "0")

        self.assertIsNone(self.service.get_note_detail(2))
        self.assertIn("笔记已删除。", output)
        self.assertIn("搜索结果", output)
        self.assertIn("已退出程序。", output)

    def test_detail_delete_cancellation_keeps_the_note_open(self) -> None:
        """Cancelled deletion retains the note and redisplays its detail page."""
        output = self._run_cli("2", "1", "2", "n", "0", "0", "0")

        self.assertIsNotNone(self.service.get_note_detail(1))
        self.assertIn("已取消删除。", output)
        self.assertGreaterEqual(output.count("笔记详情"), 2)

    def test_main_menu_edit_selects_a_note_from_the_list(self) -> None:
        """Main-menu editing selects a target from the displayed note list."""
        output = self._run_cli(
            "4",
            "1",
            "列表选择后的标题",
            "列表选择后的正文",
            "更新",
            "0",
        )

        note = self.service.get_note_detail(1)
        self.assertEqual(note["title"], "列表选择后的标题")
        self.assertEqual(note["content"], "列表选择后的正文")
        self.assertIn("选择要编辑的笔记", output)
        self.assertIn("笔记已更新。", output)

    def test_main_menu_delete_selects_a_note_from_search_results(self) -> None:
        """Main-menu deletion accepts an original number from search results."""
        output = self._run_cli("5", "s", "python", "2", "y", "0")

        self.assertIsNone(self.service.get_note_detail(2))
        self.assertIsNotNone(self.service.get_note_detail(1))
        self.assertIn("选择要删除的搜索结果", output)
        self.assertIn("笔记已删除。", output)

    def test_main_menu_action_selection_can_be_cancelled_with_zero(self) -> None:
        """Zero cancels target selection without changing any note data."""
        output = self._run_cli("4", "0", "0")

        self.assertEqual(len(self.service.list_notes()), 2)
        self.assertIn("选择要编辑的笔记", output)
        self.assertIn("已退出程序。", output)

    def test_main_menu_action_selection_handles_invalid_number(self) -> None:
        """An invalid target number can be corrected without deleting data."""
        output = self._run_cli("5", "99", "1", "n", "0")

        self.assertEqual(len(self.service.list_notes()), 2)
        self.assertIn("未找到该编号的笔记。", output)
        self.assertIn("已取消删除。", output)

    def _run_cli(self, *responses: str) -> str:
        """Run the CLI with scripted input and return its visible output."""
        output = io.StringIO()
        response_iterator = iter(responses)

        with patch(
            "builtins.input",
            side_effect=lambda _prompt: next(response_iterator),
        ):
            with redirect_stdout(output):
                self.cli.run()

        return output.getvalue()
