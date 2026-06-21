# V1.0 Evidence Policy

<!--
  Defines: evidence grading, attribution rules, source priority,
  how to handle conflicting evidence, and the "do not guess" policy.
  This is binding — all SKILL.md answers and script outputs must comply.
-->

## Evidence grades (strongest to weakest)

| Grade | Label | Definition | When to use |
|---|---|---|---|
| **L1** | 本人明确表述 | Subject's own words in a verified source, with confirmed attribution and exact location (page/paragraph) | Gold standard for all answers |
| **L2** | 基于原文的转述 | Paraphrase of the subject's words that preserves original meaning, with source location | When exact quote is too long or requires context |
| **L3** | 媒体概括 | Journalist's summary, headline, or label — may simplify or reframe | Use only as supplementary, must label as journalist/outlet wording |
| **L4** | 搜索线索/待核验线索 | Search snippet, secondary mention, or unverified lead | Use only as research direction, never as fact |
| **L5** | 项目推断 | Logical deduction from verified evidence | Must explicitly label as "推断", must state premises |
| **L6** | 证据不足 | No verified evidence exists | Must say "当前语料不足，不能确认" |

## Attribution rules

### Rule 1: Never upgrade the grade
A journalist headline must never be presented as the subject's own words. A project inference must never be stated as fact.

### Rule 2: Always locate the source
Every claim must trace back to a specific source_id and location (page/paragraph/timestamp). If you cannot locate it, you cannot use it.

### Rule 3: Preserve original meaning
When paraphrasing (L2), the paraphrase must be checkable against the original text. Do not add qualifiers, hedge words, or interpretive gloss not present in the original.

### Rule 4: Label the speaker
Every quoted or paraphrased statement must clearly attribute WHO said it: the subject (金梓才), a journalist (named), a media outlet, or the project.

### Rule 5: Handle conflicting evidence explicitly
When two verified sources appear to conflict:
1. Check dates — the subject may have changed their view
2. Check context — different questions, different funds, different market conditions
3. If still conflicting after context check, present both with dates and let the reader judge
4. Never suppress one side to make a cleaner narrative

### Rule 6: Time-bound all statements
Every claim must include the date it was stated. Views evolve. A 2022 statement may not represent 2025 views.

### Rule 7: Fund-scope all statements
When a statement is tied to a specific fund (e.g., 财通价值动量), note it. Statements about one fund do not automatically apply to all funds the manager runs.

## Source priority tiers

| Tier | source_origin_type | Weight in disputes | Example |
|---|---|---|---|
| **A** | official_report | Highest | 年报、中报、季报 — legally filed, manager-signed |
| **A** | official_profile | Highest | 基金公司官网经理简介 |
| **B** | original_interview | High | 记者直接采访，由采访媒体首发 |
| **B** | authorized_reprint | High | 经授权的转载，内容与原文一致 |
| **C** | ordinary_reprint | Medium | 第三方转载，内容可能被截断或改动 |
| **D** | other | Low | 无法确认来源的内容 |

## Rules for specific scenarios

### When a media label conflicts with the subject's own words
The subject's own words always win. Record both: "媒体标签为X，但本人原话为Y"。

### When a subject's earlier statement conflicts with a later statement
The later statement is current. Record the evolution: "2022年表述为X，2025年修正为Y"。

### When a subject's stated method conflicts with observed behavior
This is the consistency layer's job. Flag it as a consistency case study. Do not resolve it — present the evidence on both sides.

### When we only have one side of a comparison
For claims about "what he always does" or "what he never does" — if we have < 3 verified sources across < 2 years, downgrade to L5 (项目推断) with explicit caveat about limited temporal coverage.

### When asked to confirm a negative
"Cannot confirm he never does X" is the correct answer when we lack exhaustive evidence. "当前语料中未见X" is acceptable if we've checked all verified sources. "他从不X" requires proof of absence, which we almost never have.

## The "do not guess" policy

These are hard stops. When any of these conditions are met, the answer MUST include "当前语料不足，不能确认":

1. No verified source addresses the question
2. Only metadata_only sources address it (正文未核验)
3. The claim comes from a search snippet without full text verification
4. The attribution to 金梓才 cannot be confirmed (e.g., co-authored report, unclear speaker in interview transcript)
5. The statement is about performance, holdings, or fund size without dated report data

## Investment advice statement

Every output that references specific investment views, industries, or companies MUST include:

> 本文仅供研究与学习，不构成投资建议。所有观点陈述均基于公开材料，标注日期和出处。过往观点不代表未来表现。

## Citation format

### In SKILL.md answers
```
"引用文字"（source_id，verified，日期，§章节，页码）
```

### In corpus verification records
```
> 原文摘录（不超过研究所需最小长度）
>
> — source_id，页码/段落，日期
```

### In claims
```
claim_text + (source_id, verified/unverified, location)
```

## Evidence sufficiency thresholds

| Question type | Minimum evidence | Preferred evidence |
|---|---|---|
| Method framework | 2+ verified sources, 2+ years | 3+ verified, cross-year |
| Industry view | 1+ verified source with date | 2+ sources showing consistency or evolution |
| Word-deed comparison | 1 method claim + 1 behavior record | 3+ pairs across time |
| Media label audit | The media article + the subject's own words on same topic | Multiple verified sources on same topic |
| "Did he say X?" | Full-text search of all verified sources | — |
| "Does he always X?" | Requires exhaustive evidence — almost never answerable | — |
