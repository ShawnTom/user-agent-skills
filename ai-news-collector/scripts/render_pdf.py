#!/usr/bin/env python3
"""Render a new PDF through Pandoc and Chrome without overwriting output."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    skill_dir = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--template", type=Path, default=skill_dir / "assets" / "pdf-editorial.html")
    parser.add_argument("--chrome")
    return parser.parse_args()


def find_chrome(explicit: str | None) -> str | None:
    candidates = [
        explicit,
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def main() -> int:
    args = parse_args()
    errors = []
    if not args.input.is_file() or args.input.stat().st_size == 0:
        errors.append(f"input Markdown is missing or empty: {args.input}")
    if not args.template.is_file():
        errors.append(f"template not found: {args.template}")
    if args.output.exists():
        errors.append(f"refusing to overwrite existing output: {args.output}")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        errors.append("pandoc not found")
    chrome = find_chrome(args.chrome)
    if not chrome:
        errors.append("Chrome/Chromium not found")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="ai-news-pdf-", dir=args.output.parent) as temp_dir:
            html = Path(temp_dir) / "report.html"
            pandoc_cmd = [
                pandoc,
                str(args.input),
                "--from=markdown+fenced_divs+pipe_tables",
                "--standalone",
                f"--template={args.template}",
                f"--metadata=title:{args.title}",
                f"--output={html}",
            ]
            subprocess.run(pandoc_cmd, check=True, capture_output=True, text=True)
            chrome_cmd = [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={args.output}",
                html.resolve().as_uri(),
            ]
            subprocess.run(chrome_cmd, check=True, capture_output=True, text=True)
        if not args.output.is_file() or args.output.stat().st_size < 10_000:
            raise RuntimeError("generated PDF is missing or unexpectedly small")
        if args.output.read_bytes()[:4] != b"%PDF":
            raise RuntimeError("output does not have a PDF signature")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        if args.output.exists():
            args.output.unlink()
        detail = str(exc)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            detail = exc.stderr.strip()
        print(json.dumps({"ok": False, "error": detail}, ensure_ascii=False, indent=2))
        return 1

    print(
        json.dumps(
            {"ok": True, "output": str(args.output), "bytes": args.output.stat().st_size},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
