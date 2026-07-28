"""Data models and validation rules for notes."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4


@dataclass
class Note:
    """A single note stored by the application."""

    id: str
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str
    is_archived: bool = False

    @classmethod
    def create(
        cls, title: str, content: str, tags: Iterable[str] | None = None
    ) -> "Note":
        """Build a new note with an ID and timestamps."""
        clean_title = cls.clean_title(title)
        now = datetime.now(timezone.utc).isoformat()
        clean_tags = cls.clean_tags(tags or [])
        return cls(
            id=str(uuid4()),
            title=clean_title,
            content=content.strip(),
            tags=clean_tags,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict[str, object]:
        """Convert the note into JSON-compatible data."""
        return asdict(self)

    @staticmethod
    def clean_title(title: str) -> str:
        """Remove surrounding whitespace and require a non-empty title."""
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Note title cannot be empty.")
        return clean_title

    @staticmethod
    def clean_tags(tags: Iterable[str]) -> list[str]:
        """Remove blank and duplicate tags while keeping their order."""
        clean_tags: list[str] = []
        for tag in tags:
            clean_tag = tag.strip()
            if clean_tag and clean_tag not in clean_tags:
                clean_tags.append(clean_tag)
        return clean_tags
