#!/usr/bin/env python
"""
Build claims index from verified corpus files.

Reads verified sources from references/corpus/files/ and extracts claim atoms.
Currently human-driven: reads the pre-built claims/index.jsonl and validates it.
Future: may auto-extract claims from corpus using NLP.

Usage:
  python scripts/build_claims.py           # validate existing claims index
  python scripts/build_claims.py --stats   # print statistics only
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "references" / "claims"
CLAIMS_INDEX = CLAIMS_DIR / "index.jsonl"

CLAIM_TYPES = {
    "industry_view", "company_selection", "portfolio_adjustment",
    "risk_warning", "error_correction", "market_outlook",
    "method_statement", "valuation_view", "supply_demand_view", "other",
}

ATTRIBUTIONS = {"本人原话", "原文概括", "媒体概括", "项目推断"}
CONFIDENCES = {"high", "medium", "low"}
EXTRACTED_BY = {"human", "script", "hybrid"}


def read_claims(path: Path = CLAIMS_INDEX) -> list[dict]:
    records = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def validate_claims(records: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ids_seen: set[str] = set()

    for rec in records:
        cid = rec.get("claim_id", "???")

        # Required fields
        required = ["claim_id", "claim_type", "claim_text", "source_id",
                    "source_location", "attribution", "date_stated",
                    "subject_entity", "confidence", "evidence_basis",
                    "extracted_by", "extracted_date", "reviewed"]
        for field in required:
            if field not in rec:
                errors.append(f"{cid}: missing required field: {field}")

        # Unique ID
        if cid in ids_seen:
            errors.append(f"{cid}: duplicate claim_id")
        ids_seen.add(cid)

        # Enum validation
        if rec.get("claim_type") not in CLAIM_TYPES:
            errors.append(f"{cid}: invalid claim_type: {rec.get('claim_type')}")
        if rec.get("attribution") not in ATTRIBUTIONS:
            errors.append(f"{cid}: invalid attribution: {rec.get('attribution')}")
        if rec.get("confidence") not in CONFIDENCES:
            errors.append(f"{cid}: invalid confidence: {rec.get('confidence')}")
        if rec.get("extracted_by") not in EXTRACTED_BY:
            errors.append(f"{cid}: invalid extracted_by: {rec.get('extracted_by')}")

        # Text length
        text = rec.get("claim_text", "")
        if len(text) < 10:
            errors.append(f"{cid}: claim_text too short ({len(text)} chars)")
        if len(text) > 200:
            warnings.append(f"{cid}: claim_text long ({len(text)} chars)")

        # Evidence basis should not be empty for high-confidence claims
        if rec.get("confidence") == "high" and not rec.get("evidence_basis"):
            errors.append(f"{cid}: high confidence but no evidence_basis")

        # Reviewed flag
        if not rec.get("reviewed"):
            warnings.append(f"{cid}: not yet reviewed")

    return errors, warnings


def print_stats(records: list[dict]):
    print(f"Total claims: {len(records)}")
    print(f"By type:")
    for ctype, count in Counter(r["claim_type"] for r in records).most_common():
        print(f"  {ctype}: {count}")
    print(f"By attribution:")
    for attr, count in Counter(r["attribution"] for r in records).most_common():
        print(f"  {attr}: {count}")
    print(f"By confidence:")
    for conf, count in Counter(r["confidence"] for r in records).most_common():
        print(f"  {conf}: {count}")
    print(f"By source:")
    for sid, count in Counter(r["source_id"] for r in records).most_common():
        print(f"  {sid}: {count}")
    reviewed = sum(1 for r in records if r.get("reviewed"))
    print(f"Reviewed: {reviewed}/{len(records)}")


def main() -> int:
    stats_only = "--stats" in sys.argv

    records = read_claims()
    if not records:
        print("No claims found. Run build_claims.py after creating claims/index.jsonl.")
        return 1

    print_stats(records)

    if stats_only:
        return 0

    errors, warnings = validate_claims(records)
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("PASS: claims schema and cross-references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
