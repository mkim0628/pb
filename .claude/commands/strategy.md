---
description: Generate portfolio-wide strategy (3 scenarios) tailored to your holdings, with after-tax recommendations.
argument-hint: "[optional focus, e.g., 'reduce US tech exposure']"
---

Use the Agent tool with `subagent_type: "portfolio-manager"`:

> "Build a portfolio-wide strategy. Read portfolio.yaml. Dispatch market-analysts for ALL markets in my portfolio (parallel). Dispatch fundamental-analyst for each holding (parallel, batched per market). Run chart-analyst for each holding. Then run financial-advisor with all reports + portfolio.yaml to produce 3 scenarios. Then run tax-advisor for after-tax ranking. Return final markdown with scenarios, recommended actions, account routing, and sources. Optional user focus: $ARGUMENTS"

Display the supervisor's final answer.
