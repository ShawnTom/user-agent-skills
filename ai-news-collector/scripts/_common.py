#!/usr/bin/env python3
"""Shared helpers for ai-news-collector validation scripts."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class ValidationError(Exception):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValidationError(f"file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValidationError(f"{path}:{line_number}: expected JSON object")
        value["_line"] = line_number
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            clean = {key: value for key, value in row.items() if key != "_line"}
            handle.write(json.dumps(clean, ensure_ascii=False, sort_keys=True) + "\n")


def parse_iso(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label}: missing ISO-8601 timestamp")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError(f"{label}: invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValidationError(f"{label}: timezone offset is required: {value}")
    return parsed


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def require_fields(row: dict[str, Any], fields: Iterable[str], label: str) -> list[str]:
    errors = []
    for field in fields:
        if field not in row or row[field] in (None, "", []):
            errors.append(f"{label}: missing {field}")
    return errors


def print_summary(name: str, passed: bool, **details: Any) -> None:
    payload = {"validator": name, "passed": passed, **details}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
