# Fund Data Schema

## Fields

| Field | Type | Description |
|---|---|---|
| fund_code | string | Primary fund code (e.g. 720001) |
| fund_name | string | Full fund name |
| fund_type | string | 混合型/股票型 etc. |
| share_classes | list[object] | Share class info (A/C) |
| inception_date | string | Fund inception date |
| benchmark | string | Performance benchmark |
| management_company | string | Fund management company |
| custodian | string | Fund custodian bank |
| manager_name | string | Current fund manager |
| manager_tenure_start | string | Manager start date |
| manager_tenure_end | string/null | Manager end date (null if current) |
| manager_background | string | Manager bio |
| investment_objective | string | Fund investment objective |
| holdings_snapshots | list[object] | Periodic holdings data |
| holdings_snapshots[].report_date | string | Report date |
| holdings_snapshots[].report_type | string | 年报/中报/季报 |
| holdings_snapshots[].source_id | string | Source reference |
| holdings_snapshots[].top_holdings | list[object] | Top 10 holdings |
| holdings_snapshots[].top_holdings[].stock_code | string | Stock code |
| holdings_snapshots[].top_holdings[].stock_name | string | Stock name |
| holdings_snapshots[].top_holdings[].weight_pct | float | Weight in % |
| holdings_snapshots[].sector_focus | string | Primary sector theme |
| holdings_snapshots[].nav | float/null | Net asset value per share |
| data_date | string | Date this file was last updated |

## Limitations

- No performance/return data (out of scope)
- Holdings only from verified reports
- No daily NAV or flow data
- Single fund only (财通价值动量)
