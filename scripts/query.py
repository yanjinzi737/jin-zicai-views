#!/usr/bin/env python
"""
Local query CLI for jin-zicai-views.

Usage:
  python scripts/query.py search <keyword>            full-text search across all layers
  python scripts/query.py claim [--type TYPE]         list/filter claims
  python scripts/query.py method [--level LEVEL]      list/filter method rules
  python scripts/query.py timeline [--year YEAR]      show timeline entries
  python scripts/query.py fund                        show fund summary
  python scripts/query.py source <source_id>          show source details
  python scripts/query.py stats                       show corpus statistics
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYERS = {
    "corpus": ROOT / "references" / "corpus" / "index.jsonl",
    "claims": ROOT / "references" / "claims" / "index.jsonl",
    "rules": ROOT / "references" / "method_rules" / "index.jsonl",
    "consistency": ROOT / "references" / "consistency" / "index.jsonl",
    "fund": ROOT / "references" / "funds" / "720001.json",
}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cmd_search(keyword: str):
    """Full-text search across corpus, claims, rules."""
    kw = keyword.lower()
    results = []

    # Search corpus
    for rec in read_jsonl(LAYERS["corpus"]):
        text = json.dumps(rec, ensure_ascii=False).lower()
        if kw in text:
            results.append(("corpus", rec["source_id"], rec.get("title", ""), rec.get("verification_status", "")))

    # Search claims
    for rec in read_jsonl(LAYERS["claims"]):
        text = json.dumps(rec, ensure_ascii=False).lower()
        if kw in text:
            results.append(("claim", rec["claim_id"], rec.get("claim_text", ""), rec.get("confidence", "")))

    # Search rules
    for rec in read_jsonl(LAYERS["rules"]):
        text = json.dumps(rec, ensure_ascii=False).lower()
        if kw in text:
            results.append(("rule", rec["rule_id"], rec.get("rule_text", ""), rec.get("confidence", "")))

    if not results:
        print(f"No results for: {keyword}")
        return

    print(f"Found {len(results)} results for '{keyword}':\n")
    for layer, rid, text, extra in results:
        print(f"  [{layer}] {rid}")
        print(f"    {text[:120]}")
        if extra:
            print(f"    ({extra})")
        print()


def cmd_claim(claim_type: str | None = None):
    """List claims, optionally filtered by type."""
    claims = read_jsonl(LAYERS["claims"])
    if claim_type:
        claims = [c for c in claims if c.get("claim_type") == claim_type]
    for c in claims:
        print(f"{c['claim_id']} [{c['claim_type']}] ({c['confidence']})")
        print(f"  {c['claim_text']}")
        print(f"  source: {c['source_id']} | {c['attribution']} | {c['date_stated']}")
        print()


def cmd_method(level: str | None = None):
    """List method rules, optionally filtered by decision level."""
    rules = read_jsonl(LAYERS["rules"])
    if level:
        rules = [r for r in rules if r.get("decision_level") == level]
    for r in rules:
        cross = " [cross-year]" if r.get("cross_year_confirmed") else ""
        print(f"{r['rule_id']} [{r['decision_level']}] ({r['confidence']}){cross}")
        print(f"  {r['rule_text']}")
        if r.get("wording_note"):
            print(f"  note: {r['wording_note'][:100]}")
        print()


def cmd_timeline(year: str | None = None):
    """Show timeline from references/timeline.md, optionally filtered."""
    timeline_path = ROOT / "references" / "timeline.md"
    if not timeline_path.exists():
        print("timeline.md not found")
        return
    text = timeline_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = not year or year in line
        if in_section and line.startswith("- source_id"):
            print(line.strip())


def cmd_fund():
    """Show fund summary."""
    fund_path = LAYERS["fund"]
    if not fund_path.exists():
        print("Fund data not found")
        return
    fund = json.loads(fund_path.read_text(encoding="utf-8"))
    print(f"Fund: {fund['fund_name']} ({fund['fund_code']})")
    print(f"Manager: {fund['manager_name']} (since {fund['manager_tenure_start']})")
    print(f"Type: {fund['fund_type']}")
    print(f"Benchmark: {fund['benchmark']}")
    print(f"\nSnapshots ({len(fund['holdings_snapshots'])}):")
    for s in fund["holdings_snapshots"]:
        n_holdings = len(s.get("top_holdings", []))
        nav = s.get("nav", {})
        nav_str = f" NAV A={nav.get('A', '?')}" if nav else ""
        print(f"  {s['report_date']} ({s['report_type']}): {n_holdings} holdings{nav_str}")
        if s.get("top_holdings"):
            for h in s["top_holdings"][:5]:
                print(f"    {h['stock_code']} {h['stock_name']}: {h['weight_pct']}%")


def cmd_source(source_id: str):
    """Show detailed info for a source."""
    for rec in read_jsonl(LAYERS["corpus"]):
        if rec["source_id"] == source_id:
            print(f"Source: {rec['source_id']}")
            print(f"Title: {rec.get('title', '')}")
            print(f"Date: {rec.get('publication_date', '')}")
            print(f"Origin: {rec.get('source_origin_type', '')} | Quality: {rec.get('source_quality', '')}")
            print(f"Status: {rec.get('verification_status', '')} | Manager: {rec.get('manager_signed', '')}")
            print(f"Publisher: {rec.get('publisher', '')}")
            print(f"\nSummary: {rec.get('summary', '')[:300]}")
            print(f"\nExcerpt: {rec.get('relevant_excerpt', '')[:300]}")
            return
    print(f"Source not found: {source_id}")


def cmd_stats():
    """Show corpus and layer statistics."""
    corpus = read_jsonl(LAYERS["corpus"])
    claims = read_jsonl(LAYERS["claims"])
    rules = read_jsonl(LAYERS["rules"])
    consistency = read_jsonl(LAYERS["consistency"])

    print("=== Corpus ===")
    status = Counter(r["verification_status"] for r in corpus)
    for s, c in status.most_common():
        print(f"  {s}: {c}")
    quality = Counter(r.get("source_quality", "?") for r in corpus)
    print(f"  quality: {dict(quality)}")
    years = sorted(set(r.get("publication_date", "")[:4] for r in corpus if r.get("publication_date")))
    print(f"  years: {years}")

    print(f"\n=== Claims: {len(claims)} ===")
    ctypes = Counter(c["claim_type"] for c in claims)
    for t, n in ctypes.most_common():
        print(f"  {t}: {n}")

    print(f"\n=== Method Rules: {len(rules)} ===")
    levels = Counter(r["decision_level"] for r in rules)
    for l, n in levels.most_common():
        print(f"  {l}: {n}")
    cross = sum(1 for r in rules if r.get("cross_year_confirmed"))
    print(f"  cross-year confirmed: {cross}")

    print(f"\n=== Consistency: {len(consistency)} ===")
    clabels = Counter(c["consistency_label"] for c in consistency)
    for l, n in clabels.most_common():
        print(f"  {l}: {n}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: query.py search <keyword>")
            return
        cmd_search(sys.argv[2])
    elif cmd == "claim":
        ctype = None
        if len(sys.argv) > 2 and sys.argv[2] == "--type":
            ctype = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_claim(ctype)
    elif cmd == "method":
        level = None
        if len(sys.argv) > 2 and sys.argv[2] == "--level":
            level = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_method(level)
    elif cmd == "timeline":
        year = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].startswith("--year=") else None
        if year:
            year = year.split("=")[1]
        cmd_timeline(year)
    elif cmd == "fund":
        cmd_fund()
    elif cmd == "source":
        if len(sys.argv) < 3:
            print("Usage: query.py source <source_id>")
            return
        cmd_source(sys.argv[2])
    elif cmd == "stats":
        cmd_stats()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
