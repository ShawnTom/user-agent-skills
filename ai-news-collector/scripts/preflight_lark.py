#!/usr/bin/env python3
"""Read-only Lark authentication, Wiki ACL, content, and cite-chain preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_USER_SCOPES = {
    "wiki:node:read",
    "wiki:node:retrieve",
    "docs:document.content:read",
    "docx:document:readonly",
    "offline_access",
}
ERROR_MARKERS = (
    "sign in",
    "login required",
    "permission denied",
    "access denied",
    "unauthorized",
    "验证码",
    "登录后查看",
    "无权限",
)
CITE_RE = re.compile(r'<cite\b[^>]*\bdoc-id="([A-Za-z0-9]+)"[^>]*>', re.IGNORECASE)


class PreflightError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", required=True)
    parser.add_argument("--identity", choices=("user", "bot"), default="user")
    parser.add_argument("--sample-cites", type=int, default=3)
    parser.add_argument("--min-chars", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--lark-cli", default="lark-cli")
    return parser.parse_args()


def parse_json_output(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    candidates = []
    for position, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, consumed = decoder.raw_decode(text[position:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            trailing = text[position + consumed :].strip()
            if not trailing:
                return value
            candidates.append((consumed, value))
    if not candidates:
        raise PreflightError("CLI returned no JSON object")
    return max(candidates, key=lambda item: item[0])[1]


def run_json(command: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
    env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
    process = subprocess.run(command, text=True, capture_output=True, env=env, check=False)
    combined = "\n".join(part for part in (process.stdout, process.stderr) if part)
    if process.returncode != 0:
        try:
            payload = parse_json_output(combined)
            error = payload.get("error", {})
            message = error.get("message") or combined.strip()
            hint = error.get("hint")
            if hint:
                message = f"{message}; hint: {hint}"
        except PreflightError:
            message = combined.strip() or f"exit code {process.returncode}"
        raise PreflightError(message)
    return parse_json_output(combined)


def auth_status(cli: str) -> dict[str, Any]:
    return run_json([cli, "auth", "status", "--json", "--verify"])


def fetch_doc(cli: str, doc: str, identity: str) -> dict[str, Any]:
    return run_json(
        [
            cli,
            "docs",
            "+fetch",
            "--doc",
            doc,
            "--as",
            identity,
            "--doc-format",
            "markdown",
            "--detail",
            "simple",
            "--scope",
            "full",
            "--format",
            "json",
        ]
    )


def validate_auth(payload: dict[str, Any], identity: str, after_fetch: bool = False) -> dict[str, Any]:
    if not payload.get("verified"):
        raise PreflightError("auth status is not verified")
    record = payload.get("identities", {}).get(identity, {})
    if not record.get("verified"):
        raise PreflightError(f"{identity} identity is not server-verified")
    if identity == "user":
        scopes = set(str(record.get("scope", "")).split())
        missing = sorted(REQUIRED_USER_SCOPES - scopes)
        if missing:
            raise PreflightError("missing user scopes: " + ", ".join(missing))
        acceptable = {"ready"} if after_fetch else {"ready", "needs_refresh"}
        if record.get("status") not in acceptable:
            raise PreflightError(f"unexpected user status: {record.get('status')}")
        token_acceptable = {"valid"} if after_fetch else {"valid", "needs_refresh"}
        if record.get("tokenStatus") not in token_acceptable:
            raise PreflightError(f"unexpected tokenStatus: {record.get('tokenStatus')}")
    return {
        "status": record.get("status"),
        "token_status": record.get("tokenStatus"),
        "verified": bool(record.get("verified")),
        "expires_at": record.get("expiresAt"),
        "refresh_expires_at": record.get("refreshExpiresAt"),
    }


def document_data(payload: dict[str, Any], identity: str, min_chars: int) -> tuple[dict[str, Any], str]:
    if payload.get("ok") is not True:
        raise PreflightError("document fetch did not return ok=true")
    if payload.get("identity") != identity:
        raise PreflightError(f"document returned identity={payload.get('identity')}, expected {identity}")
    document = payload.get("data", {}).get("document", {})
    content = document.get("content")
    if not isinstance(content, str) or len(content) < min_chars:
        raise PreflightError(f"document content is too short: {len(content or '')} chars")
    lowered = content[:2000].casefold()
    marker = next((item for item in ERROR_MARKERS if item in lowered), None)
    if marker:
        raise PreflightError(f"document content contains an error-page marker: {marker}")
    if not isinstance(document.get("revision_id"), int) or document["revision_id"] <= 0:
        raise PreflightError("document revision_id must be positive")
    return document, content


def main() -> int:
    args = parse_args()
    if args.sample_cites < 0:
        print(json.dumps({"ok": False, "error": "sample-cites must be non-negative"}, ensure_ascii=False))
        return 2
    try:
        before = validate_auth(auth_status(args.lark_cli), args.identity)
        node_payload = run_json(
            [
                args.lark_cli,
                "wiki",
                "+node-get",
                "--node-token",
                args.doc,
                "--as",
                args.identity,
                "--format",
                "json",
            ]
        )
        if node_payload.get("ok") is not True or node_payload.get("identity") != args.identity:
            raise PreflightError("Wiki node resolution failed or returned the wrong identity")
        node = node_payload.get("data", {})
        if node.get("obj_type") != "docx":
            raise PreflightError(f"Wiki object must be docx, got {node.get('obj_type')}")

        main_payload = fetch_doc(args.lark_cli, args.doc, args.identity)
        document, content = document_data(main_payload, args.identity, args.min_chars)
        if node.get("obj_token") and document.get("document_id") != node.get("obj_token"):
            raise PreflightError("Wiki obj_token does not match fetched document_id")

        cite_ids = list(dict.fromkeys(CITE_RE.findall(content)))
        if args.sample_cites > 0 and not cite_ids:
            raise PreflightError("document contains no cite doc-id values to sample")
        samples = []
        for doc_id in cite_ids[: args.sample_cites]:
            child_url = f"https://waytoagi.feishu.cn/wiki/{doc_id}"
            child_payload = fetch_doc(args.lark_cli, child_url, args.identity)
            child, child_content = document_data(child_payload, args.identity, 100)
            samples.append(
                {
                    "doc_id": doc_id,
                    "document_id": child.get("document_id"),
                    "revision_id": child.get("revision_id"),
                    "content_chars": len(child_content),
                    "content_sha256": hashlib.sha256(child_content.encode("utf-8")).hexdigest(),
                }
            )
        required_samples = min(args.sample_cites, len(cite_ids))
        if len(samples) != required_samples:
            raise PreflightError("not all requested cite samples were readable")

        after = validate_auth(auth_status(args.lark_cli), args.identity, after_fetch=True)
        audit = {
            "ok": True,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "identity": args.identity,
            "auth_before": before,
            "auth_after": after,
            "wiki": {
                "title": node.get("title"),
                "node_token": node.get("node_token"),
                "obj_token": node.get("obj_token"),
                "obj_type": node.get("obj_type"),
                "updated_at": node.get("updated_at"),
            },
            "document": {
                "document_id": document.get("document_id"),
                "revision_id": document.get("revision_id"),
                "content_chars": len(content),
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "cite_count": len(cite_ids),
            },
            "cite_samples": samples,
        }
        if args.output:
            if args.output.exists():
                raise PreflightError(f"refusing to overwrite audit file: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 0
    except (OSError, PreflightError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
