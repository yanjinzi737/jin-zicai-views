# V1.0 Data Model

<!--
  Defines all entity types, field schemas, and relationships.
  This is the authoritative schema reference — if code and docs disagree, this file wins.
-->

## Design principle

**Separate what a source IS from how well we've CHECKED it.** The current index.jsonl conflates `source_type` (origin) with `primary_source` (priority signal) and `verification_status` (check level). V1.0 splits these into independent axes.

## Entity layers

```
corpus/           sources (index.jsonl)     ← what we have, where it came from
claims/           claim atoms               ← specific statements extracted from sources
method_rules/     decision rules            ← patterns abstracted from claims
consistency/      comparisons               ← claims vs. behavior over time
funds/            fund profiles & holdings  ← institutional context
```

## Layer 1: Corpus (sources)

### source_origin_type (never changes after classification)

| Value | Definition | Priority tier |
|---|---|---|
| `official_report` | 法定报告：年报、中报、季报、招募说明书 | A |
| `original_interview` | 原创新闻采访，由采访媒体首发 | B |
| `authorized_reprint` | 经原出处授权的转载 | B |
| `ordinary_reprint` | 未经明确授权的第三方转载（新浪、天天基金等） | C |
| `official_profile` | 基金公司官网发布的经理简介/资料 | A |
| `other` | 以上均不适用 | D |

### verification_status (can change as we verify)

| Value | Definition |
|---|---|
| `verified` | 已完成正文级核验，基金经理归属确认，关键摘录已保存 |
| `pending` | 已获取正文，核验进行中 |
| `metadata_only` | 仅有 URL 和标题等元信息，正文未获取 |
| `restricted` | 正文获取受限（付费墙、区域限制等） |
| `failed` | 核验尝试失败（文件损坏、编码不可解等） |
| `inaccessible` | URL 失效或无法访问 |
| `rejected` | 经评估不适合收录（内容不相关、质量过低等） |

### source_priority (derived from source_origin_type + verification_status)

- A + verified = strongest evidence
- C + metadata_only = weakest usable lead
- Priority affects: default sort order in query results, weight in automated consistency checks

### New fields to add to index.jsonl

```json
{
  "source_origin_type": "official_report | original_interview | authorized_reprint | ordinary_reprint | official_profile | other",
  "original_publication": "原始出处名称（如转载，填原出处）",
  "original_url": "原始出处的 URL（如可获取）",
  "original_authors": "原作者/记者姓名",
  "access_type": "official_site | third_party_reprint | pdf_download | other",
  "access_url": "实际访问的 URL",
  "content_scope": "full_text | excerpt | abstract_only",
  "subject_confirmed": "confirmed | inferred | unconfirmed",
  "date_published": "2022-08-02",
  "date_accessed": "2026-06-21",
  "language": "zh-CN",
  "source_quality": "A | B | C | D"
}
```

### Migration: JZC-2022-INTERVIEW-004

Before (conflated):
```json
"source_type": "media_interview_reprint",
"primary_source": true
```

After (separated):
```json
"source_origin_type": "ordinary_reprint",
"original_publication": "证券时报",
"original_authors": "詹晨、赵梦桥",
"original_date": "2022-08-02",
"access_type": "third_party_reprint",
"access_url": "https://finance.sina.com.cn/money/fund/jjzl/2022-08-02/doc-imizirav7732226.shtml",
"verification_status": "verified",
"source_quality": "B"
```

Note: source_quality is B (not C) because the CONTENT is an original interview — the reprint is the access method, not the content provenance. We preserve both facts: origin via original_* fields, access via access_* fields.

## Layer 2: Claims

### claim_index.jsonl schema

```json
{
  "claim_id": "CL-001",
  "claim_type": "industry_view | company_selection | portfolio_adjustment | risk_warning | error_correction | market_outlook | method_statement | valuation_view | supply_demand_view | other",
  "claim_text": "精炼后的主张文本（25-80字）",
  "source_id": "JZC-2025-ANNUAL-001",
  "source_location": "§4.5, 第15页",
  "attribution": "本人原话 | 原文概括 | 媒体概括 | 项目推断",
  "date_stated": "2025-03-28",
  "subject_entity": "金梓才",
  "subject_fund": "财通价值动量",
  "industry_tags": ["AI", "半导体"],
  "confidence": "high | medium | low",
  "evidence_basis": "引用的原文摘录（≤80字）",
  "negation_of": "CL-XXX（如为修正此前观点）",
  "extracted_by": "human | script | hybrid",
  "extracted_date": "2026-06-21",
  "reviewed": true
}
```

### claim_type definitions

| claim_type | What it captures | Example |
|---|---|---|
| `industry_view` | 对具体行业/赛道/产业链的判断 | "海外AI算力处于景气上行期" |
| `company_selection` | 选股标准或个股判断 | "寻找成长确定性高、股价空间大的优质公司" |
| `portfolio_adjustment` | 仓位调整、行业超配/低配 | "二季度从国内算力转向海外算力" |
| `risk_warning` | 对风险因素的提示 | "需关注芯片出口管制政策变化" |
| `error_correction` | 公开修正此前判断 | "修正一季度国内算力超配判断" |
| `market_outlook` | 对市场整体的展望 | "A股市场整体估值处于历史中低位" |
| `method_statement` | 对自身投资方法的陈述 | "以产业研究为基础，做好行业中观配置轮动" |
| `valuation_view` | 对估值水平的判断 | "当前估值已反映较多悲观预期" |
| `supply_demand_view` | 对供给/需求格局的判断 | "AI芯片供给紧张，需求持续超预期" |
| `other` | 以上均不适用 | — |

## Layer 3: Method rules

### method_rules_index.jsonl schema

```json
{
  "rule_id": "MR-001",
  "decision_level": "industry | company | portfolio | risk | review",
  "rule_text": "规则陈述（一句话）",
  "source_claim_ids": ["CL-001", "CL-005"],
  "source_ids": ["JZC-2025-ANNUAL-001", "JZC-2022-INTERVIEW-004"],
  "cross_year_confirmed": true,
  "wording_stable": true,
  "wording_note": "2022年\"动态优化\"→2025年\"动态变化\"",
  "contradicted_by": ["CL-XXX（如有）"],
  "confidence": "high | medium | low",
  "extracted_date": "2026-06-21"
}
```

### decision_level definitions

| Level | Scope | Example rule |
|---|---|---|
| `industry` | 行业选择逻辑 | 优先选择景气度向上拐点的行业 |
| `company` | 个股选择逻辑 | 在正确赛道中寻找成长确定性高、股价空间大的公司 |
| `portfolio` | 组合管理逻辑 | 根据公司基本面的动态变化调整持仓 |
| `risk` | 风险控制逻辑 | —（当前语料不足） |
| `review` | 回顾/修正逻辑 | 公开修正产业判断错误 |

## Layer 4: Consistency

```json
{
  "comparison_id": "CS-001",
  "claim_id": "CL-001",
  "behavior_source_id": "JZC-2025-H1-REPORT-001",
  "behavior_description": "持仓/操作描述",
  "consistency_label": "consistent | compatible | inconsistent | insufficient_data | not_testable",
  "evidence": "一致性判断依据",
  "checked_date": "2026-06-21"
}
```

## Layer 5: Fund data

```json
{
  "fund_code": "720001",
  "fund_name": "财通价值动量混合",
  "fund_type": "混合型",
  "manager_name": "金梓才",
  "manager_tenure_start": "2015-07-15",
  "manager_tenure_end": null,
  "holdings_snapshots": [
    {
      "report_date": "2025-06-30",
      "report_type": "中报",
      "top_holdings": [
        {"stock_code": "xxxxxx", "stock_name": "某公司", "weight_pct": 8.5}
      ],
      "source_id": "JZC-2025-H1-REPORT-001"
    }
  ]
}
```

## Relationships

```
corpus/index.jsonl (1) ────< (N) claims/index.jsonl
claims/index.jsonl (N) ────< (N) method_rules/index.jsonl
claims/index.jsonl (1) ────< (N) consistency/index.jsonl
corpus/index.jsonl (1) ────< (N) funds/720001.json (holdings_snapshots[].source_id)
```

## Field migration plan

The existing `corpus_common.py` FIELDS tuple (22 fields) will be extended, not replaced. Old field names will be retained as aliases with deprecation warnings. The `scripts/migrate_v1_source_type.py` script will:

1. Read all 12 records from index.jsonl
2. Add new fields (source_origin_type, original_*, access_*, etc.)
3. Populate from existing data where possible
4. Write back with old fields preserved as deprecated_* aliases
5. Validate no records lost in migration
