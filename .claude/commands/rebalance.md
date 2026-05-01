---
description: Rebalance recommendation — bring portfolio toward target allocation given current drift, market view, and tax cost.
argument-hint: "[optional target, e.g., 'KR 30 / US 50 / Asia 20']"
---

Use the Agent tool with `subagent_type: "portfolio-manager"`:

> "Generate a rebalancing plan. Read portfolio.yaml; compute current allocation drift vs target (use $ARGUMENTS if provided, otherwise derive from profile.risk_tolerance). Dispatch market-analysts for affected markets. Then financial-advisor builds the rebalance trades. Then tax-advisor minimizes the tax cost of rebalancing (prefer trims in losing positions, sells in tax-advantaged accounts, etc.). Return markdown:
>   - Current vs target allocation table
>   - Trade list with after-tax cost
>   - Suggested execution order
>   - Estimated tax bill if executed entirely this year vs split across years"

Display the result.
