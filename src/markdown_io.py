"""Convert note records to and from the project's Markdown format."""

import json
from typing import Any, Mapping


_METADATA_FIELDS = ("title", "tags", "created_at", "updated_at")


def note_to_markdown(note: Mapping[str, Any]) -> str:
    """Return one note as Markdown with a small JSON-based metadata header."""
    title = _require_string(note, "title")
    content = _require_string(note, "content")
    created_at = _require_string(note, "created_at")
    updated_at = _require_string(note, "updated_at")
    tags = note.get("tags")
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("Markdown export error: tags must be a list of strings.")

    metadata_lines = [
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f"created_at: {json.dumps(created_at, ensure_ascii=False)}",
        f"updated_at: {json.dumps(updated_at, ensure_ascii=False)}",
        "---",
    ]
    return "\n".join(metadata_lines) + "\n\n" + content


def markdown_to_note(markdown_text: str) -> dict[str, Any]:
    """Parse a Markdown document produced by :func:`note_to_markdown`."""
    if not isinstance(markdown_text, str):
        raise ValueError("Markdown import error: content must be text.")

    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("Markdown import error: metadata must start with '---'.")

    try:
        closing_index = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(
            "Markdown import error: metadata closing '---' is missing."
        ) from error

    if closing_index + 1 >= len(lines) or lines[closing_index + 1] != "":
        raise ValueError(
            "Markdown import error: a blank line is required after metadata."
        )

    metadata = _parse_metadata(lines[1:closing_index])
    content = "\n".join(lines[closing_index + 2 :])
    return {"content": content, **metadata}


def _parse_metadata(metadata_lines: list[str]) -> dict[str, Any]:
    """Read and validate the fixed metadata lines in a Markdown header."""
    metadata: dict[str, Any] = {}
    for line in metadata_lines:
        key, separator, raw_value = line.partition(": ")
        if not separator or not key:
            raise ValueError(
                "Markdown import error: metadata lines must use 'field: value'."
            )
        if key in metadata:
            raise ValueError(f"Markdown import error: duplicate metadata field '{key}'.")
        try:
            metadata[key] = json.loads(raw_value)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Markdown import error: metadata field '{key}' is invalid."
            ) from error

    missing_fields = [field for field in _METADATA_FIELDS if field not in metadata]
    if missing_fields:
        raise ValueError(
            "Markdown import error: missing metadata fields: "
            + ", ".join(missing_fields)
            + "."
        )

    unexpected_fields = set(metadata) - set(_METADATA_FIELDS)
    if unexpected_fields:
        raise ValueError("Markdown import error: unsupported metadata field found.")

    for field in ("title", "created_at", "updated_at"):
        if not isinstance(metadata[field], str):
            raise ValueError(f"Markdown import error: '{field}' must be a string.")
    if not isinstance(metadata["tags"], list) or not all(
        isinstance(tag, str) for tag in metadata["tags"]
    ):
        raise ValueError(
            "Markdown import error: 'tags' must be a list of strings."
        )

    return metadata


def _require_string(note: Mapping[str, Any], field: str) -> str:
    """Return a required string field from a note, or explain the export error."""
    value = note.get(field)
    if not isinstance(value, str):
        raise ValueError(f"Markdown export error: '{field}' must be a string.")
    return value
