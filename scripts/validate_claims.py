#!/usr/bin/env python
"""
Validate claims/index.jsonl schema, cross-references, and consistency.

Usage:
  python scripts/validate_claims.py
  python scripts/validate_claims.py --strict   # also check source_id references exist
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS_INDEX = ROOT / "references" / "claims" / "index.jsonl"
CORPUS_INDEX = ROOT / "references" / "corpus" / "index.jsonl"

CLAIM_TYPES = {
    "industry_view", "company_selection", "portfolio_adjustment",
    "risk_warning", "error_correction", "market_outlook",
    "method_statement", "valuation_view", "supply_demand_view", "other",
}

ATTRIBUTIONS = {"本人原话", "原文概括", "媒体概括", "项目推断"}
CONFIDENCES = {"high", "medium", "low"}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main() -> int:
    strict = "--strict" in sys.argv

    claims = read_jsonl(CLAIMS_INDEX)
    if not claims:
        print("ERROR: no claims found")
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    # Load corpus for cross-reference check
    corpus_ids: set[str] = set()
    if strict:
        corpus = read_jsonl(CORPUS_INDEX)
        corpus_ids = {r["source_id"] for r in corpus}

    for rec in claims:
        cid = rec.get("claim_id", "???")

        # Schema validation
        for field in ["claim_id", "claim_type", "claim_text", "source_id",
                      "source_location", "attribution", "date_stated",
                      "subject_entity", "confidence", "evidence_basis"]:
            if not rec.get(field):
                errors.append(f"{cid}: empty required field: {field}")

        if rec.get("claim_type") not in CLAIM_TYPES:
            errors.append(f"{cid}: invalid claim_type: {rec.get('claim_type')}")
        if rec.get("attribution") not in ATTRIBUTIONS:
            errors.append(f"{cid}: invalid attribution: {rec.get('attribution')}")
        if rec.get("confidence") not in CONFIDENCES:
            errors.append(f"{cid}: invalid confidence: {rec.get('confidence')}")

        # Cross-reference to corpus
        if strict and rec.get("source_id") not in corpus_ids:
            errors.append(f"{cid}: source_id not in corpus: {rec.get('source_id')}")

        # Content checks
        evidence = rec.get("evidence_basis", "")
        claim_text = rec.get("claim_text", "")
        if len(evidence) > 200:
            warnings.append(f"{cid}: evidence_basis is {len(evidence)} chars")

        # Method statements should be 本人原话 for high confidence
        if rec.get("claim_type") == "method_statement" and rec.get("confidence") == "high":
            if rec.get("attribution") != "本人原话":
                warnings.append(f"{cid}: high-confidence method_statement not 本人原话")

        # Error corrections should have negation_of
        if rec.get("claim_type") == "error_correction" and not rec.get("negation_of"):
            warnings.append(f"{cid}: error_correction without negation_of")

    # Duplicate IDs
    ids = [r["claim_id"] for r in claims]
    for cid, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate claim_id: {cid} ({count})")

    # ID format
    for rec in claims:
        cid = rec["claim_id"]
        if not cid.startswith("CL-") or not cid[3:].isdigit():
            errors.append(f"{cid}: invalid claim_id format (expected CL-XXX)")

    # Summary
    print(f"claims={len(claims)}")
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("PASS: claims validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
