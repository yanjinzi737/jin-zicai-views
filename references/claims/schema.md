# Claims Schema

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| claim_id | string | yes | Unique ID: `CL-XXX` |
| claim_type | enum | yes | One of 10 claim types |
| claim_text | string | yes | Distilled claim (25-120 chars) |
| source_id | string | yes | Source reference (e.g. JZC-2025-ANNUAL-001) |
| source_location | string | yes | Location in source (§, page, paragraph) |
| attribution | enum | yes | 本人原话 / 原文概括 / 媒体概括 / 项目推断 |
| date_stated | string | yes | YYYY-MM-DD when stated |
| subject_entity | string | yes | Person who made the claim |
| subject_fund | string | no | Fund associated with claim |
| industry_tags | list[str] | no | Industry/theme tags |
| confidence | enum | yes | high / medium / low |
| evidence_basis | string | yes | Source excerpt (≤120 chars) |
| negation_of | string | no | claim_id this negates (for corrections) |
| extracted_by | enum | yes | human / script / hybrid |
| extracted_date | string | yes | YYYY-MM-DD |
| reviewed | bool | yes | Has been human-reviewed |

## claim_type values

- `industry_view`: Judgment about specific industry/sector/chain
- `company_selection`: Stock selection criteria or individual stock views
- `portfolio_adjustment`: Position changes, sector over/underweight
- `risk_warning`: Risk factor alerts
- `error_correction`: Public correction of prior view
- `market_outlook`: Overall market outlook
- `method_statement`: Statement about own investment method
- `valuation_view`: Judgment about valuation levels
- `supply_demand_view`: Judgment about supply/demand dynamics
- `other`: None of the above

## attribution values

- `本人原话`: Subject's exact words in verified source
- `原文概括`: Paraphrase by project from verified source text
- `媒体概括`: Journalist/media summary or headline
- `项目推断`: Project inference from evidence (must label as 推断)

## confidence values

- `high`: Directly stated in verified source, unambiguous
- `medium`: Reasonably inferred from verified source
- `low`: Weak signal, single source, or requires interpretation
