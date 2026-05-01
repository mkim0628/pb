---
description: Update investor profile (risk_tolerance, horizon_years, base_currency).
argument-hint: "[--risk conservative|moderate|aggressive] [--horizon N] [--currency KRW|USD]"
---

Parse `$ARGUMENTS` and run:
```
python scripts/update_portfolio.py profile [--risk X] [--horizon N] [--currency C]
```

Then read `portfolio.yaml` and print the updated `profile` block.

If no arguments, just show the current profile.
