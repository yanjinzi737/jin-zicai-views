# Method Rules Schema

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| rule_id | string | yes | Unique ID: `MR-XXX` |
| decision_level | enum | yes | industry / company / portfolio / risk / review |
| rule_text | string | yes | Rule statement (one sentence) |
| source_claim_ids | list[str] | yes | Supporting claim IDs |
| source_ids | list[str] | yes | Underlying source IDs |
| cross_year_confirmed | bool | yes | Confirmed across multiple years |
| wording_stable | bool | yes | Wording consistent across sources |
| wording_note | string | no | Note on wording evolution |
| contradicted_by | list[str] | no | Claim IDs that contradict this rule |
| confidence | enum | yes | high / medium / low |
| extracted_date | string | yes | YYYY-MM-DD |

## decision_level values

- `industry`: Industry/sector selection logic
- `company`: Company selection logic
- `portfolio`: Portfolio management logic
- `risk`: Risk control logic
- `review`: Review/correction logic

## confidence values

- `high`: Supported by 3+ verified sources across 2+ years, wording stable
- `medium`: Supported by 2+ verified sources, some wording variation
- `low`: Single source or significant wording variation
