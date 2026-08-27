"""Tests for the project's Markdown note format."""

import unittest

from src.markdown_io import markdown_to_note, note_to_markdown


class MarkdownIoTestCase(unittest.TestCase):
    """Verify note records can round-trip through the Markdown format."""

    def setUp(self) -> None:
        self.note = {
            "id": "note-1",
            "title": "Python 学习计划",
            "content": "# 今天的任务\n\n- 学习 `unittest`\n- 复习 SQLite",
            "tags": ["Python", "学习,计划"],
            "created_at": "2026-08-27T10:00:00+00:00",
            "updated_at": "2026-08-27T11:00:00+00:00",
            "is_archived": False,
        }

    def test_note_to_markdown_writes_metadata_and_content(self) -> None:
        """Exported Markdown contains the required header and original body."""
        markdown_text = note_to_markdown(self.note)

        self.assertIn('title: "Python 学习计划"', markdown_text)
        self.assertIn('tags: ["Python", "学习,计划"]', markdown_text)
        self.assertIn('created_at: "2026-08-27T10:00:00+00:00"', markdown_text)
        self.assertTrue(markdown_text.endswith(self.note["content"]))

    def test_markdown_round_trip_preserves_exported_note_fields(self) -> None:
        """Project Markdown parses back to the same importable note data."""
        parsed_note = markdown_to_note(note_to_markdown(self.note))

        self.assertEqual(
            parsed_note,
            {
                "title": self.note["title"],
                "content": self.note["content"],
                "tags": self.note["tags"],
                "created_at": self.note["created_at"],
                "updated_at": self.note["updated_at"],
            },
        )

    def test_markdown_to_note_rejects_missing_metadata_delimiter(self) -> None:
        """A missing closing delimiter produces an actionable error."""
        with self.assertRaisesRegex(ValueError, "closing '---' is missing"):
            markdown_to_note('---\ntitle: "标题"')

    def test_markdown_to_note_rejects_missing_required_metadata(self) -> None:
        """Incomplete headers are rejected instead of silently using defaults."""
        markdown_text = "---\ntitle: \"标题\"\ntags: []\n---\n\n正文"

        with self.assertRaisesRegex(ValueError, "missing metadata fields"):
            markdown_to_note(markdown_text)

    def test_markdown_to_note_rejects_invalid_tag_metadata(self) -> None:
        """Tag metadata must remain a JSON list of strings."""
        markdown_text = (
            "---\n"
            'title: "标题"\n'
            'tags: "标签"\n'
            'created_at: "2026-08-27T10:00:00+00:00"\n'
            'updated_at: "2026-08-27T11:00:00+00:00"\n'
            "---\n\n正文"
        )

        with self.assertRaisesRegex(ValueError, "tags.*list of strings"):
            markdown_to_note(markdown_text)

    def test_note_to_markdown_rejects_invalid_note_data(self) -> None:
        """Export fails clearly when a required field has the wrong type."""
        invalid_note = dict(self.note, tags="Python")

        with self.assertRaisesRegex(ValueError, "tags must be a list of strings"):
            note_to_markdown(invalid_note)
