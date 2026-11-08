# Current run status

**Status checked/published:** Nov 08, 2026 at 02:27:24 AM EST (UTC-0500)

**Latest workflow or disposition event:** Nov 08, 2026 at 02:27:24 AM EST (UTC-0500)

**running**

| Job | Model | State | Started (Eastern) | Ended (Eastern) |
|---|---|---|---|---|
| 0-supervisor | z-ai/glm-5.3-flash | returned requires cross review | Nov 08, 2026 at 02:23:56 AM EST (UTC-0500) | Nov 08, 2026 at 02:25:56 AM EST (UTC-0500) |
| 0-worker | google/gemma-4-31b-it | returned requires cross review | Nov 08, 2026 at 02:23:56 AM EST (UTC-0500) | Nov 08, 2026 at 02:25:56 AM EST (UTC-0500) |
| 1-supervisor | openai/gpt-6.1-terra | returned requires cross review | Nov 08, 2026 at 02:25:57 AM EST (UTC-0500) | Nov 08, 2026 at 02:27:24 AM EST (UTC-0500) |
| 1-worker | google/gemma-4-31b-it | returned requires cross review | Nov 08, 2026 at 02:25:57 AM EST (UTC-0500) | Nov 08, 2026 at 02:27:24 AM EST (UTC-0500) |

Real registered GLM/Terra supervisors and Gemma worker. Intentional waiting-client disconnect once per disposable workflow; no application code, task outcomes or corrective primary-run feedback.

A returned job is not yet reviewed or qualified. A blocked job needs diagnosis; its original endpoint is preserved. This queue cannot start calibration or scored runs.

All displayed times use America/New_York, automatically switching between EST and EDT. UTC timestamps remain in the machine-readable record. This page updates automatically at job transitions and on explicit status refreshes. A newer status-check timestamp does not imply new agent work. It is not a live heartbeat. No chat/push/email notification is configured. [Machine-readable status](launch.json).
