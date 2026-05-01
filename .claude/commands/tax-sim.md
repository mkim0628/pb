---
description: Simulate tax impact of a hypothetical trade plan without executing.
argument-hint: "[plan description, e.g., 'sell 50 005930 at 80000, buy 10 NVDA at 120']"
---

Use the Agent tool with `subagent_type: "tax-advisor"` directly (skip Tier 1):

> "Simulate the tax impact of: $ARGUMENTS. Read portfolio.yaml for current holdings (cost basis), data/tax_rules/*.yaml for rules, and the recent ledger for YTD realized gains. Compute capital gains tax, dividend impact, transaction costs. Suggest:
>  - Optimal account routing
>  - Better timing (e.g., wait until Jan to delay tax year)
>  - Loss harvesting pairs
>  - Cross-market routing alternatives (TSMC ADR vs TWSE, etc.)
> Return markdown with before/after numbers and execution_order."

Display the result.
