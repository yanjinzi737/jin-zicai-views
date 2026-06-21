# Consistency Schema

## Fields

| Field | Type | Description |
|---|---|---|
| comparison_id | string | Unique ID: CS-XXX |
| claim_id | string | Claim being tested |
| behavior_source_id | string | Source showing behavior |
| behavior_description | string | What was observed |
| consistency_label | enum | consistent/compatible/inconsistent/insufficient_data/not_testable |
| evidence | string | Evidence for the consistency judgment |
| checked_date | string | YYYY-MM-DD |

## consistency_label values

- `consistent`: Behavior directly matches stated claim
- `compatible`: Behavior does not contradict claim but linkage is indirect
- `inconsistent`: Behavior contradicts stated claim
- `insufficient_data`: Not enough data to compare
- `not_testable`: Claim is not testable with available data
