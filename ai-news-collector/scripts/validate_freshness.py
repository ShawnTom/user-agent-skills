#!/usr/bin/env python3
"""Validate publication and continuation timestamps against the report window."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import ValidationError, load_jsonl, parse_iso, print_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--start", required=True, help="exclusive ISO-8601 window start")
    parser.add_argument("--cutoff", required=True, help="inclusive ISO-8601 cutoff")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        start = parse_iso(args.start, "window_start")
        cutoff = parse_iso(args.cutoff, "cutoff")
        sources = load_jsonl(args.sources)
    except ValidationError as exc:
        print_summary("freshness", False, errors=[str(exc)])
        return 2

    if start >= cutoff:
        errors.append("window_start must be earlier than cutoff")

    counts = {"current": 0, "continuation": 0, "historical": 0}
    for source in sources:
        label = f"source line {source['_line']} ({source.get('source_id', 'unknown')})"
        role = source.get("temporal_role", "current")
        if role not in counts:
            errors.append(f"{label}: invalid temporal_role {role}")
            continue
        counts[role] += 1
        try:
            published = parse_iso(source.get("published_at"), f"{label}.published_at")
            retrieved = parse_iso(source.get("retrieved_at"), f"{label}.retrieved_at")
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if retrieved < published:
            errors.append(f"{label}: retrieved_at is earlier than published_at")

        waytoagi_day = (
            source.get("source_type") == "waytoagi"
            and source.get("time_precision") == "day"
            and source.get("date_basis") == "waytoagi_latest_heading"
        )
        if role == "current" and waytoagi_day:
            if not (start.date() <= published.date() <= cutoff.date()):
                errors.append(
                    f"{label}: WaytoAGI heading date is outside the report calendar-date window"
                )
        elif role == "current" and not (start < published <= cutoff):
            errors.append(f"{label}: current source published_at is outside (start, cutoff]")
        elif role == "continuation":
            try:
                latest = parse_iso(source.get("latest_update_at"), f"{label}.latest_update_at")
            except ValidationError as exc:
                errors.append(str(exc))
                continue
            if not (start < latest <= cutoff):
                errors.append(f"{label}: continuation latest_update_at is outside (start, cutoff]")
        elif role == "historical" and source.get("headline_eligible", False):
            errors.append(f"{label}: historical source cannot be headline_eligible")

    print_summary(
        "freshness",
        not errors,
        window_start=start.isoformat(),
        cutoff=cutoff.isoformat(),
        sources=len(sources),
        roles=counts,
        errors=errors,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
