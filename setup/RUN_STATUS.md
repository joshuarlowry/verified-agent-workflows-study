# Current run status

**Status checked/published:** Nov 07, 2026 at 12:19:34 PM EST (UTC-0500)

**Latest workflow or disposition event:** Nov 07, 2026 at 12:19:34 PM EST (UTC-0500)

**running**

| Job | Model | State | Started (Eastern) | Ended (Eastern) |
|---|---|---|---|---|
| terra-revision | openai/gpt-6.1-terra | returned requires cross review | Nov 07, 2026 at 12:14:37 PM EST (UTC-0500) | Nov 07, 2026 at 12:19:32 PM EST (UTC-0500) |
| gemma-cross-review | google/gemma-4-31b-it | running | Nov 07, 2026 at 12:19:34 PM EST (UTC-0500) | — |

Fresh Terra scope revision followed sequentially by fresh Gemma cross-review. Every input tree is checked using the actual mounted subject UID before model calls. No calibration/scoring dispatch.

A returned job is not yet reviewed or qualified. A blocked job needs diagnosis; its original endpoint is preserved. This queue cannot start calibration or scored runs.

All displayed times use America/New_York, automatically switching between EST and EDT. UTC timestamps remain in the machine-readable record. This page updates automatically at job transitions and on explicit status refreshes. A newer status-check timestamp does not imply new agent work. It is not a live heartbeat. No chat/push/email notification is configured. [Machine-readable status](launch.json).
