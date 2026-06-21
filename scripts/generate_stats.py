#!/usr/bin/env python
"""
Generate statistics for README.md and SKILL.md.

Reads all data layers and outputs current stats as markdown tables.
Can be run manually or in CI to keep stats up-to-date.

Usage:
  python scripts/generate_stats.py                # print stats
  python scripts/generate_stats.py --update-readme # update README.md
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = datetime.now().strftime("%Y-%m-%d")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def get_stats() -> dict:
    corpus = read_jsonl(ROOT / "references" / "corpus" / "index.jsonl")
    claims = read_jsonl(ROOT / "references" / "claims" / "index.jsonl")
    rules = read_jsonl(ROOT / "references" / "method_rules" / "index.jsonl")
    consistency = read_jsonl(ROOT / "references" / "consistency" / "index.jsonl")

    status = Counter(r["verification_status"] for r in corpus)
    quality = Counter(r.get("source_quality", "?") for r in corpus)
    origins = Counter(r.get("source_origin_type", "?") for r in corpus)

    claim_types = Counter(c["claim_type"] for c in claims)
    attributions = Counter(c["attribution"] for c in claims)

    rule_levels = Counter(r["decision_level"] for r in rules)
    rule_conf = Counter(r["confidence"] for r in rules)
    cross_year = sum(1 for r in rules if r.get("cross_year_confirmed"))

    consistency_labels = Counter(c["consistency_label"] for c in consistency)

    years = sorted(set(
        r.get("publication_date", "")[:4]
        for r in corpus if r.get("publication_date")
    ))

    return {
        "date": TODAY,
        "total_sources": len(corpus),
        "verified": status.get("verified", 0),
        "pending": status.get("pending", 0),
        "metadata_only": status.get("metadata_only", 0),
        "inaccessible": status.get("inaccessible", 0),
        "quality_a": quality.get("A", 0),
        "quality_b": quality.get("B", 0),
        "years": years,
        "year_min": years[0] if years else "?",
        "year_max": years[-1] if years else "?",
        "total_claims": len(claims),
        "claim_types": dict(claim_types),
        "attributions": dict(attributions),
        "total_rules": len(rules),
        "rule_levels": dict(rule_levels),
        "rule_conf": dict(rule_conf),
        "cross_year_rules": cross_year,
        "total_consistency": len(consistency),
        "consistency_labels": dict(consistency_labels),
        "origin_types": dict(origins),
    }


def print_stats(stats: dict):
    print(f"Stats as of {stats['date']}:")
    print(f"  Sources: {stats['total_sources']} total ({stats['verified']} verified, "
          f"{stats['pending']} pending, {stats['inaccessible']} inaccessible)")
    print(f"  Quality: A={stats['quality_a']}, B={stats['quality_b']}")
    print(f"  Years: {stats['year_min']}–{stats['year_max']}")
    print(f"  Claims: {stats['total_claims']} ({stats['attributions']})")
    print(f"  Rules: {stats['total_rules']} ({stats['cross_year_rules']} cross-year)")
    print(f"  Consistency: {stats['total_consistency']} ({stats['consistency_labels']})")


def update_readme(stats: dict):
    readme_path = ROOT / "README.md"
    if not readme_path.exists():
        print("README.md not found")
        return

    content = readme_path.read_text(encoding="utf-8")

    # Update source stats table
    source_table = f"""| 状态 | 数量 |
|---|---|
| verified | {stats['verified']} |
| pending | {stats['pending']} |
| inaccessible | {stats['inaccessible']} |
| **总计** | **{stats['total_sources']}** |"""

    content = re.sub(
        r"\| 状态 \| 数量 \|[\s\S]*?\|\*\*总计\*\* \| \*\*\d+\*\* \|",
        source_table,
        content,
    )

    # Update last update date
    content = re.sub(
        r"最近的更新日期.*",
        f"最近的更新日期：{stats['date']}（自动生成）",
        content,
    )

    readme_path.write_text(content, encoding="utf-8")
    print(f"Updated README.md with stats as of {stats['date']}")


def main():
    stats = get_stats()
    print_stats(stats)

    if "--update-readme" in sys.argv:
        update_readme(stats)


if __name__ == "__main__":
    main()
