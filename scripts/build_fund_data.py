#!/usr/bin/env python
"""
Build/validate fund data from verified corpus sources.

Reads references/funds/720001.json and validates against corpus index.
Prints fund summary and holdings timeline.

Usage:
  python scripts/build_fund_data.py           # validate fund data
  python scripts/build_fund_data.py --summary # fund summary only
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNDS_DIR = ROOT / "references" / "funds"
CORPUS_INDEX = ROOT / "references" / "corpus" / "index.jsonl"


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    summary_only = "--summary" in sys.argv

    fund = read_json(FUNDS_DIR / "720001.json")
    if not fund:
        print("ERROR: 720001.json not found")
        return 1

    corpus_records: list[dict] = []
    if CORPUS_INDEX.exists():
        for line in CORPUS_INDEX.read_text(encoding="utf-8").splitlines():
            if line.strip():
                corpus_records.append(json.loads(line))

    corpus_ids = {r["source_id"] for r in corpus_records}

    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    for field in ["fund_code", "fund_name", "manager_name", "manager_tenure_start"]:
        if not fund.get(field):
            errors.append(f"missing required field: {field}")

    # Holdings snapshots
    snapshots = fund.get("holdings_snapshots", [])
    if not snapshots:
        warnings.append("no holdings snapshots")

    for snap in snapshots:
        sid = snap.get("source_id", "")
        if sid and sid not in corpus_ids:
            errors.append(f"holdings source_id not in corpus: {sid}")

        # Validate holding weights
        holdings = snap.get("top_holdings", [])
        if holdings:
            total = sum(h["weight_pct"] for h in holdings)
            if total > 100:
                errors.append(f"{snap['report_date']}: holdings weight sum {total}% > 100%")

    # Summary
    print(f"Fund: {fund['fund_name']} ({fund['fund_code']})")
    print(f"Manager: {fund['manager_name']} (since {fund['manager_tenure_start']})")
    print(f"Holdings snapshots: {len(snapshots)}")
    for snap in snapshots:
        holdings_n = len(snap.get("top_holdings", []))
        nav_info = ""
        if snap.get("nav"):
            nav_info = f" NAV A={snap['nav'].get('A', '?')} C={snap['nav'].get('C', '?')}"
        print(f"  {snap['report_date']} ({snap['report_type']}): {holdings_n} holdings, {snap['sector_focus'][:80]}...{nav_info}")

    if summary_only:
        return 0

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("PASS: fund data validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
