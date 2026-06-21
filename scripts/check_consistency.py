#!/usr/bin/env python
"""
Check claim-behavior consistency comparisons.

Validates consistency/index.jsonl against claims and corpus.

Usage:
  python scripts/check_consistency.py
  python scripts/check_consistency.py --stats   # statistics only
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSISTENCY_INDEX = ROOT / "references" / "consistency" / "index.jsonl"
CLAIMS_INDEX = ROOT / "references" / "claims" / "index.jsonl"
CORPUS_INDEX = ROOT / "references" / "corpus" / "index.jsonl"

LABELS = {"consistent", "compatible", "inconsistent", "insufficient_data", "not_testable"}


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

    comparisons = read_jsonl(CONSISTENCY_INDEX)
    if not comparisons:
        print("ERROR: no consistency comparisons found")
        return 1

    claims = read_jsonl(CLAIMS_INDEX)
    claim_ids = {c["claim_id"] for c in claims}
    corpus = read_jsonl(CORPUS_INDEX)
    corpus_ids = {r["source_id"] for r in corpus}

    errors: list[str] = []
    warnings: list[str] = []

    for comp in comparisons:
        cid = comp.get("comparison_id", "???")

        for field in ["comparison_id", "claim_id", "behavior_source_id",
                      "behavior_description", "consistency_label", "evidence"]:
            if not comp.get(field):
                errors.append(f"{cid}: empty required field: {field}")

        if comp.get("consistency_label") not in LABELS:
            errors.append(f"{cid}: invalid consistency_label: {comp.get('consistency_label')}")

        if comp.get("claim_id") not in claim_ids:
            errors.append(f"{cid}: claim_id not found: {comp.get('claim_id')}")

        if comp.get("behavior_source_id") not in corpus_ids:
            errors.append(f"{cid}: behavior_source_id not in corpus: {comp.get('behavior_source_id')}")

    # Stats
    print(f"Comparisons: {len(comparisons)}")
    for lbl, count in Counter(c["consistency_label"] for c in comparisons).most_common():
        print(f"  {lbl}: {count}")
    print(f"Claims tested: {len(set(c['claim_id'] for c in comparisons))}")
    print(f"Sources used: {len(set(c['behavior_source_id'] for c in comparisons))}")

    if stats_only:
        return 0

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("PASS: consistency validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
