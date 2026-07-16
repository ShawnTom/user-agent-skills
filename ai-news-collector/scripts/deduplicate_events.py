#!/usr/bin/env python3
"""Merge exact event keys and reject unresolved near-duplicate events."""

from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

from _common import ValidationError, load_jsonl, normalize_text, print_summary, require_fields, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--similarity", type=float, default=0.92)
    return parser.parse_args()


def merge_unique(left: list, right: list) -> list:
    return list(dict.fromkeys([*left, *right]))


def main() -> int:
    args = parse_args()
    try:
        events = load_jsonl(args.input)
    except ValidationError as exc:
        print_summary("deduplicate_events", False, errors=[str(exc)])
        return 2

    errors: list[str] = []
    by_key: dict[str, dict] = {}
    exact_merges = 0
    for event in events:
        label = f"event line {event['_line']}"
        errors.extend(require_fields(event, ("event_id", "canonical_key", "title", "entity", "published_at", "source_ids"), label))
        key = str(event.get("canonical_key", "")).strip()
        if not key:
            continue
        if key not in by_key:
            by_key[key] = event.copy()
            continue
        existing = by_key[key]
        existing["source_ids"] = merge_unique(existing.get("source_ids", []), event.get("source_ids", []))
        existing["claim_ids"] = merge_unique(existing.get("claim_ids", []), event.get("claim_ids", []))
        existing["merged_event_ids"] = merge_unique(
            existing.get("merged_event_ids", [existing.get("event_id")]), [event.get("event_id")]
        )
        exact_merges += 1

    merged = list(by_key.values())
    suspects = []
    for index, left in enumerate(merged):
        for right in merged[index + 1 :]:
            if normalize_text(str(left.get("entity", ""))) != normalize_text(str(right.get("entity", ""))):
                continue
            score = SequenceMatcher(
                None,
                normalize_text(str(left.get("title", ""))),
                normalize_text(str(right.get("title", ""))),
            ).ratio()
            if score >= args.similarity:
                suspects.append(
                    {
                        "left": left.get("event_id"),
                        "right": right.get("event_id"),
                        "similarity": round(score, 3),
                    }
                )

    if suspects:
        errors.append("near-duplicate events require canonical_key review: " + json.dumps(suspects, ensure_ascii=False))

    if not errors:
        write_jsonl(args.output, merged)
    print_summary(
        "deduplicate_events",
        not errors,
        input_events=len(events),
        output_events=len(merged) if not errors else None,
        exact_merges=exact_merges,
        suspects=suspects,
        errors=errors,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
