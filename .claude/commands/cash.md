---
description: Adjust cash balance for an account (deposit/withdraw).
argument-hint: "[account] [delta] [currency?] [note?]"
---

Parse `$ARGUMENTS` and run:
```
python scripts/update_portfolio.py cash --account <id> --delta <amount> [--currency C] [--note "..."]
```

Confirm: "Cash {account} {delta:+,} {currency} → balance {new}".
