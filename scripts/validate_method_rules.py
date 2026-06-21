#!/usr/bin/env python
"""
Validate method_rules/index.jsonl schema, claim cross-references, and coverage.

Usage:
  python scripts/validate_method_rules.py
  python scripts/validate_method_rules.py --coverage   # check decision level coverage
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_INDEX = ROOT / "references" / "method_rules" / "index.jsonl"
CLAIMS_INDEX = ROOT / "references" / "claims" / "index.jsonl"

DECISION_LEVELS = {"industry", "company", "portfolio", "risk", "review"}
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
    coverage_flag = "--coverage" in sys.argv

    rules = read_jsonl(RULES_INDEX)
    if not rules:
        print("ERROR: no rules found")
        return 1

    claims = read_jsonl(CLAIMS_INDEX)
    claim_ids = {c["claim_id"] for c in claims}
    claim_type_count = Counter(c["claim_type"] for c in claims)

    errors: list[str] = []
    warnings: list[str] = []

    for rule in rules:
        rid = rule.get("rule_id", "???")

        # Schema
        for field in ["rule_id", "decision_level", "rule_text", "source_claim_ids", "source_ids"]:
            if not rule.get(field):
                errors.append(f"{rid}: empty required field: {field}")

        if rule.get("decision_level") not in DECISION_LEVELS:
            errors.append(f"{rid}: invalid decision_level: {rule.get('decision_level')}")
        if rule.get("confidence") not in CONFIDENCES:
            errors.append(f"{rid}: invalid confidence: {rule.get('confidence')}")

        # Cross-ref claims
        for cid in rule.get("source_claim_ids", []):
            if cid not in claim_ids:
                errors.append(f"{rid}: claim_id not found: {cid}")

        # Cross-ref contradicted_by claims
        for cid in rule.get("contradicted_by", []):
            if cid not in claim_ids:
                errors.append(f"{rid}: contradicted_by claim_id not found: {cid}")

        # Wording note should exist if wording is not stable
        if not rule.get("wording_stable") and not rule.get("wording_note"):
            warnings.append(f"{rid}: wording not stable, consider adding wording_note")

    # Duplicate IDs
    ids = [r["rule_id"] for r in rules]
    for rid, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate rule_id: {rid} ({count})")

    # ID format
    for r in rules:
        rid = r["rule_id"]
        if not rid.startswith("MR-") or not rid[3:].isdigit():
            errors.append(f"{rid}: invalid rule_id format (expected MR-XXX)")

    # Coverage
    covered_levels = {r["decision_level"] for r in rules}
    missing_levels = DECISION_LEVELS - covered_levels

    print(f"rules={len(rules)} levels={len(covered_levels)}/5")
    if missing_levels:
        print(f"Missing decision levels: {missing_levels}")

    if coverage_flag:
        print(f"\nDecision level coverage:")
        for dl in sorted(DECISION_LEVELS):
            count = sum(1 for r in rules if r["decision_level"] == dl)
            high = sum(1 for r in rules if r["decision_level"] == dl and r["confidence"] == "high")
            print(f"  {dl}: {count} rules ({high} high confidence)")
        print(f"\nClaim type coverage:")
        for ct, count in claim_type_count.most_common():
            rules_using = sum(1 for r in rules if any(
                cid in r.get("source_claim_ids", []) for cid in [
                    c["claim_id"] for c in claims if c["claim_type"] == ct
                ]
            ))
            print(f"  {ct}: {count} claims, {rules_using} rules reference them")

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("PASS: method rules validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
