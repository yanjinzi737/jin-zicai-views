#!/usr/bin/env python
"""
Build/audit method rules from claims and verified sources.

Reads references/method_rules/index.jsonl and validates against claims.
Prints statistics and quality assessment.

Usage:
  python scripts/build_method_rules.py           # validate rules
  python scripts/build_method_rules.py --stats   # statistics only
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


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main() -> int:
    stats_only = "--stats" in sys.argv

    rules = read_jsonl(RULES_INDEX)
    if not rules:
        print("ERROR: no rules found")
        return 1

    claims = read_jsonl(CLAIMS_INDEX)
    claim_ids = {c["claim_id"] for c in claims}

    errors: list[str] = []
    warnings: list[str] = []

    for rule in rules:
        rid = rule.get("rule_id", "???")

        if rule.get("decision_level") not in DECISION_LEVELS:
            errors.append(f"{rid}: invalid decision_level: {rule.get('decision_level')}")

        for cid in rule.get("source_claim_ids", []):
            if cid not in claim_ids:
                errors.append(f"{rid}: unknown claim_id: {cid}")

        if not rule.get("rule_text"):
            errors.append(f"{rid}: empty rule_text")

        cross = rule.get("cross_year_confirmed")
        if cross and rule.get("confidence") != "high":
            warnings.append(f"{rid}: cross_year_confirmed but confidence is {rule.get('confidence')}")

    # Stats
    print(f"Total rules: {len(rules)}")
    print(f"By decision level:")
    for dl, count in Counter(r["decision_level"] for r in rules).most_common():
        print(f"  {dl}: {count}")
    print(f"By confidence:")
    for conf, count in Counter(r["confidence"] for r in rules).most_common():
        print(f"  {conf}: {count}")
    cross_year = sum(1 for r in rules if r.get("cross_year_confirmed"))
    print(f"Cross-year confirmed: {cross_year}/{len(rules)}")
    wording_stable = sum(1 for r in rules if r.get("wording_stable"))
    print(f"Wording stable: {wording_stable}/{len(rules)}")

    if stats_only:
        return 0

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
