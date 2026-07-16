#!/usr/bin/env python3
"""Validate claim-level evidence instead of merely checking URL presence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from _common import ValidationError, load_jsonl, normalize_text, parse_iso, print_summary, require_fields


SOURCE_TYPES = {"official", "regulator", "media", "research", "community", "waytoagi"}
SOURCE_ROLES = {"event_page", "article", "dataset", "entry_page"}
RETRIEVAL_METHODS = {"direct_fetch", "api", "lark_cli", "search_snippet"}
CLAIM_TYPES = {
    "release",
    "policy",
    "funding",
    "market_metric",
    "benchmark",
    "customer_result",
    "document_fact",
    "analysis",
    "forecast",
}
STATUSES = {"verified", "primary_only", "conflicting", "unverified"}
HIGH_RISK = {"funding", "market_metric", "benchmark", "customer_result"}
PRIMARY_TYPES = {"official", "regulator"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--claims", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sources = load_jsonl(args.sources)
        claims = load_jsonl(args.claims)
    except ValidationError as exc:
        print_summary("claims", False, errors=[str(exc)])
        return 2

    errors: list[str] = []
    source_index = {}
    required_source_fields = (
        "source_id",
        "canonical_url",
        "title",
        "publisher",
        "independence_key",
        "source_type",
        "source_role",
        "retrieval_method",
        "published_at",
        "retrieved_at",
        "evidence_text",
        "content_sha256",
    )

    for source in sources:
        label = f"source line {source['_line']}"
        errors.extend(require_fields(source, required_source_fields, label))
        source_id = source.get("source_id")
        if source_id in source_index:
            errors.append(f"{label}: duplicate source_id {source_id}")
        elif source_id:
            source_index[source_id] = source
        parsed_url = urlparse(str(source.get("canonical_url", "")))
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors.append(f"{label}: canonical_url must be an absolute HTTP(S) URL")
        if source.get("source_type") not in SOURCE_TYPES:
            errors.append(f"{label}: invalid source_type {source.get('source_type')}")
        if source.get("source_role") not in SOURCE_ROLES:
            errors.append(f"{label}: invalid source_role {source.get('source_role')}")
        if source.get("retrieval_method") not in RETRIEVAL_METHODS:
            errors.append(f"{label}: invalid retrieval_method {source.get('retrieval_method')}")
        if not SHA256_RE.fullmatch(str(source.get("content_sha256", ""))):
            errors.append(f"{label}: content_sha256 must be 64 hexadecimal characters")
        for field in ("published_at", "retrieved_at"):
            try:
                parse_iso(source.get(field), f"{label}.{field}")
            except ValidationError as exc:
                errors.append(str(exc))

    claim_index = {}
    for claim in claims:
        label = f"claim line {claim['_line']}"
        errors.extend(require_fields(claim, ("claim_id", "event_id", "text", "claim_type", "status", "evidence"), label))
        claim_id = claim.get("claim_id")
        if claim_id in claim_index:
            errors.append(f"{label}: duplicate claim_id {claim_id}")
        elif claim_id:
            claim_index[claim_id] = claim
        claim_type = claim.get("claim_type")
        status = claim.get("status")
        if claim_type not in CLAIM_TYPES:
            errors.append(f"{label}: invalid claim_type {claim_type}")
        if status not in STATUSES:
            errors.append(f"{label}: invalid status {status}")

        included = bool(claim.get("include_in_report", True))
        if included and status == "unverified":
            errors.append(f"{label}: unverified claim cannot be included in the report")

        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}: evidence must be a non-empty list")
            continue

        evidence_sources = []
        for position, item in enumerate(evidence, 1):
            if not isinstance(item, dict):
                errors.append(f"{label}: evidence #{position} must be an object")
                continue
            source_id = item.get("source_id")
            quote = item.get("quote")
            source = source_index.get(source_id)
            if source is None:
                errors.append(f"{label}: evidence #{position} references unknown source_id {source_id}")
                continue
            if not isinstance(quote, str) or not quote.strip():
                errors.append(f"{label}: evidence #{position} has no quote")
                continue
            if normalize_text(quote) not in normalize_text(str(source.get("evidence_text", ""))):
                errors.append(f"{label}: quote for {source_id} is not present in source evidence_text")
            if source.get("source_role") == "entry_page":
                errors.append(f"{label}: entry page {source_id} cannot be used as claim evidence")
            if source.get("retrieval_method") == "search_snippet":
                errors.append(f"{label}: search snippet {source_id} cannot be used as claim evidence")
            evidence_sources.append(source)

        independence = {str(source.get("independence_key")) for source in evidence_sources}
        source_types = {str(source.get("source_type")) for source in evidence_sources}
        if included and claim_type in HIGH_RISK:
            if status not in {"verified", "conflicting"}:
                errors.append(f"{label}: {claim_type} cannot be included with status {status}")
            if len(independence) < 2:
                errors.append(f"{label}: {claim_type} requires two independent sources")
        if included and claim_type == "release" and not (source_types & {"official"}):
            errors.append(f"{label}: release requires an event-specific official source")
        if included and claim_type == "policy" and not (source_types & {"regulator"}):
            errors.append(f"{label}: policy requires a regulator source")
        if included and status == "primary_only" and not (source_types & PRIMARY_TYPES):
            errors.append(f"{label}: primary_only requires official or regulator evidence")
        if included and claim_type == "document_fact" and source_types == {"waytoagi"}:
            pass
        if included and claim_type in {"analysis", "forecast"}:
            basis = claim.get("basis_claim_ids")
            if not isinstance(basis, list) or not basis:
                errors.append(f"{label}: {claim_type} requires basis_claim_ids")
        if included and claim_type == "forecast":
            if claim.get("confidence") not in {"low", "medium", "high"}:
                errors.append(f"{label}: forecast confidence must be low, medium, or high")
            if not claim.get("horizon"):
                errors.append(f"{label}: forecast requires horizon")

    known_claims = set(claim_index)
    for claim in claims:
        for basis_id in claim.get("basis_claim_ids", []):
            if basis_id not in known_claims:
                errors.append(f"claim {claim.get('claim_id')}: unknown basis_claim_id {basis_id}")
            elif claim_index[basis_id].get("status") not in {"verified", "primary_only"}:
                errors.append(
                    f"claim {claim.get('claim_id')}: basis claim {basis_id} is not verified or primary_only"
                )

    print_summary(
        "claims",
        not errors,
        sources=len(sources),
        claims=len(claims),
        included_claims=sum(bool(row.get("include_in_report", True)) for row in claims),
        errors=errors,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
