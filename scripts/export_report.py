#!/usr/bin/env python
"""
Generate markdown research reports from the corpus and claims.

Usage:
  python scripts/export_report.py method     # methodology report
  python scripts/export_report.py industry   # industry view timeline
  python scripts/export_report.py full       # full research report
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = datetime.now().strftime("%Y-%m-%d")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def report_methodology() -> str:
    """Generate methodology research report."""
    claims = read_jsonl(ROOT / "references" / "claims" / "index.jsonl")
    rules = read_jsonl(ROOT / "references" / "method_rules" / "index.jsonl")
    consistency = read_jsonl(ROOT / "references" / "consistency" / "index.jsonl")

    method_claims = [c for c in claims if c["claim_type"] == "method_statement"]
    high_rules = [r for r in rules if r["confidence"] == "high"]

    lines = [
        "# 金梓才投资方法论研究报告",
        f"自动生成于 {TODAY}",
        "",
        "## 核心方法论陈述",
        "",
    ]

    for c in method_claims:
        lines.append(f"- **{c['claim_text']}**")
        lines.append(f"  - 来源: {c['source_id']} ({c['date_stated']})")
        lines.append(f"  - 归属: {c['attribution']}")
        lines.append("")

    lines.append("## 高置信度方法规则（跨年份确认）")
    lines.append("")
    for r in high_rules:
        lines.append(f"- **[{r['decision_level']}] {r['rule_text']}**")
        if r.get("wording_note"):
            lines.append(f"  - 措辞说明: {r['wording_note']}")
        lines.append("")

    lines.append("## 言行一致性")
    lines.append("")
    for c in consistency:
        lines.append(f"- **{c['comparison_id']}**: {c['consistency_label']}")
        lines.append(f"  - 主张: 涉及 {c['claim_id']}")
        lines.append(f"  - 行为: {c['behavior_description'][:120]}")
        lines.append(f"  - 证据: {c['evidence'][:200]}")
        lines.append("")

    lines.append("---")
    lines.append(f"*本报告仅供研究学习，不构成投资建议。数据截止 {TODAY}。*")
    return "\n".join(lines)


def report_industry() -> str:
    """Generate industry view timeline report."""
    claims = read_jsonl(ROOT / "references" / "claims" / "index.jsonl")
    industry_claims = [c for c in claims if c["claim_type"] in ("industry_view", "supply_demand_view")]
    industry_claims.sort(key=lambda c: c["date_stated"])

    lines = [
        "# 金梓才行业观点时间线",
        f"自动生成于 {TODAY}",
        "",
    ]

    for c in industry_claims:
        lines.append(f"## {c['date_stated']} | {c['claim_id']}")
        lines.append(f"**{c['claim_text']}**")
        lines.append(f"- 来源: {c['source_id']} ({c['source_location']})")
        lines.append(f"- 归属: {c['attribution']} | 置信度: {c['confidence']}")
        if c.get("industry_tags"):
            lines.append(f"- 标签: {', '.join(c['industry_tags'])}")
        if c.get("evidence_basis"):
            lines.append(f"- 原文: {c['evidence_basis'][:200]}")
        lines.append("")

    lines.append("---")
    lines.append(f"*本报告仅供研究学习，不构成投资建议。数据截止 {TODAY}。*")
    return "\n".join(lines)


def report_full() -> str:
    """Generate comprehensive research report."""
    corpus = read_jsonl(ROOT / "references" / "corpus" / "index.jsonl")
    claims = read_jsonl(ROOT / "references" / "claims" / "index.jsonl")
    rules = read_jsonl(ROOT / "references" / "method_rules" / "index.jsonl")

    verified = [r for r in corpus if r["verification_status"] == "verified"]
    high_claims = [c for c in claims if c["confidence"] == "high"]

    lines = [
        "# 金梓才公开观点研究报告（完整版）",
        f"自动生成于 {TODAY}",
        "",
        "## 数据概览",
        f"- 已验证来源: {len(verified)} 份",
        f"- 声明原子: {len(claims)} 条",
        f"- 方法规则: {len(rules)} 条",
        f"- 覆盖年份: 2022–2026",
        "",
        "## 已验证来源",
    ]

    for v in verified:
        lines.append(f"- **{v['source_id']}**: {v.get('title', '')} ({v.get('publication_date', '')})")
        lines.append(f"  - 类型: {v.get('source_origin_type', '')} | 质量: {v.get('source_quality', '')}")

    lines.append("")
    lines.append("## 高置信度声明")
    for c in high_claims:
        lines.append(f"- [{c['claim_type']}] **{c['claim_text']}** — {c['source_id']} ({c['date_stated']})")

    lines.append("")
    lines.append("---")
    lines.append(f"*本报告仅供研究学习，不构成投资建议。数据截止 {TODAY}。*")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    report_type = sys.argv[1]
    reports = {
        "method": report_methodology,
        "industry": report_industry,
        "full": report_full,
    }

    if report_type not in reports:
        print(f"Unknown report type: {report_type}")
        print(f"Available: {', '.join(reports.keys())}")
        return

    output = reports[report_type]()
    print(output)

    # Optionally save to file
    if "--save" in sys.argv:
        out_path = ROOT / "tmp" / f"report-{report_type}-{TODAY}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
