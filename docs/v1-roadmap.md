# V1.0 Roadmap

<!--
  10-phase plan to upgrade the core MVP to a full research skill.
  Entry: 4 verified sources, working SKILL.md, JSONL/CSV index.
  Exit: automated stats, CLI tools, CI/CD, fund data, claims, method rules, acceptance tested.
-->

## Phase dependency graph

```
A (architecture audit) ──┬── B (claims) ──┬── F (consistency) ──┬── J (acceptance)
                         │                │                      │
                         ├── C (rules) ───┘                      │
                         │                                       │
                         ├── D (corpus expansion) ───────────────┤
                         │                                       │
                         ├── E (fund data) ──────────────────────┤
                         │                                       │
                         └── G (CLI) ── H (CI/CD) ── I (README) ┘
```

## Phase A: Architecture audit & V1.0 plan

**Status**: in_progress
**Entry**: 4 verified sources, working corpus infrastructure
**Exit**: v1-roadmap.md, data-model.md, evidence-policy.md written; 7 audit items documented; source_origin_type separated from verification_status

Deliverables:
- `docs/v1-roadmap.md` (this file)
- `docs/data-model.md`
- `docs/evidence-policy.md`
- Migration script for source_type fix
- Commit: `docs: define v1 evidence and data architecture`

Audit checklist:
- [x] 1. What the skill can currently answer
- [x] 2. What the skill cannot currently answer
- [x] 3. Content duplication across verified sources
- [x] 4. Hardcoded stats in README/SKILL
- [x] 5. source_type vs verification_status conflation
- [x] 6. Fields insufficient for view evolution and word-deed comparison
- [x] 7. License suitability for code, docs, and structured data

## Phase B: Structured claims layer

**Status**: pending
**Entry**: Phase A complete
**Exit**: `references/claims/index.jsonl` with >= 20 claim atoms extracted from 4 verified sources

Deliverables:
- `references/claims/index.jsonl` — structured claims with 10+ claim_types
- `references/claims/schema.md` — field definitions
- `scripts/build_claims.py` — extract claims from verified corpus files
- `scripts/validate_claims.py` — validate claim schema and cross-references
- Commit: `feat: add structured claims layer with N atoms`

Claim types: industry_view, company_selection, portfolio_adjustment, risk_warning, error_correction, market_outlook, method_statement, valuation_view, supply_demand_view, other

## Phase C: Method rules

**Status**: pending
**Entry**: Phase A complete
**Exit**: `references/method_rules/index.jsonl` with >= 10 rules across 5 decision levels

Deliverables:
- `references/method_rules/index.jsonl` — structured method rules
- `references/method_rules/schema.md` — field definitions
- `scripts/build_method_rules.py` — extract rules from verified sources
- `scripts/validate_method_rules.py` — validate rule schema
- Commit: `feat: add method rules with N rules`

Decision levels: industry, company, portfolio, risk, review

## Phase D: Corpus expansion

**Status**: pending
**Entry**: Phase A complete
**Exit**: >= 8 verified sources total (up from 4), all metadata_only sources classified

Deliverables:
- Attempt body verification on 8 metadata_only sources
- Document which are accessible and which are blocked
- Upgrade verified count where possible
- Update `references/corpus/index.jsonl` and `index.csv`
- Update `references/timeline.md`
- Commit: `verify: expand corpus to N verified sources`

## Phase E: Fund data MVP

**Status**: pending
**Entry**: Phase A complete
**Exit**: `references/funds/720001.json` with holdings snapshots and manager timeline

Deliverables:
- `references/funds/720001.json` — fund profile, manager tenure, holdings snapshots
- `references/funds/schema.md` — field definitions
- `scripts/build_fund_data.py` — assemble fund data from verified reports
- Commit: `feat: add fund data MVP for 财通价值动量`

Scope: single fund (财通价值动量, 720001/021523) only. No performance data.

## Phase F: Claim-behavior consistency

**Status**: pending
**Entry**: Phases B + C + D complete
**Exit**: `references/consistency/index.jsonl` with >= 5 case studies

Deliverables:
- `references/consistency/index.jsonl` — consistency comparisons
- `references/consistency/schema.md` — field definitions
- `scripts/check_consistency.py` — automated consistency checks
- Commit: `feat: add claim-behavior consistency comparisons`

Consistency labels: consistent, compatible, inconsistent, insufficient_data, not_testable

## Phase G: Local query CLI

**Status**: pending
**Entry**: Phases B + C + F complete
**Exit**: `scripts/query.py` with 5+ query commands

Deliverables:
- `scripts/query.py` — CLI tool for querying corpus, claims, rules
- `scripts/export_report.py` — generate markdown reports from queries
- Commit: `feat: add local query CLI`

Commands: search, claim, method, timeline, consistency, fund, report

## Phase H: Automated stats & CI/CD

**Status**: pending
**Entry**: Phase G complete
**Exit**: GitHub Actions workflow passing; stats auto-generated

Deliverables:
- `scripts/generate_stats.py` — auto-generate stats for README/SKILL
- `.github/workflows/validate.yml` — CI: validate corpus, claims, rules
- `.github/workflows/stats.yml` — CI: regenerate stats on push
- Commit: `ci: add validation and stats automation`

## Phase I: README as product page

**Status**: pending
**Entry**: Phases D + E + F complete
**Exit**: README rewritten as product page with auto-generated stats

Deliverables:
- Rewrite `README.md` as product landing page
- Auto-generated stats tables (via generate_stats.py)
- Usage examples with real outputs
- Commit: `docs: rewrite README as product page`

## Phase J: Final acceptance testing

**Status**: pending
**Entry**: Phases A–I complete
**Exit**: All acceptance criteria met; V1.0 tag

Acceptance criteria:
- [ ] >= 8 verified sources
- [ ] >= 20 claim atoms with cross-references
- [ ] >= 10 method rules
- [ ] >= 5 consistency case studies
- [ ] Fund data for 720001 with >= 4 holdings snapshots
- [ ] CLI query tool with 5+ working commands
- [ ] CI passing on every push
- [ ] README with auto-generated stats
- [ ] SKILL.md updated to reference all V1 layers
- [ ] All hardcoded stats replaced with generated output
- [ ] No verified data overwritten or lost
- [ ] All scripts runnable with `python scripts/<name>.py`
- [ ] Git tag: v1.0.0
