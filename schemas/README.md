# Draft provider usage record

`provider-usage-record.schema.json` defines a final per-request provider usage snapshot. The normalizer preserves raw usage, nullable unavailable counters, actor/session/phase provenance and a stable deduplication key. Prompt input includes cache subsets; cache-creation/write aliases are selected once. Reasoning is diagnostic and never added to billed completion. Native counters and provider-resolution data remain explicitly unverified until separately joined/cross-checked; no missing field is invented as zero.

Repeated provider snapshots with the same response/run/session/source identity replace the previous snapshot rather than adding another charge. A retry with a different response ID is a different request and remains chargeable. Native step data and generation/invoice cross-checks are other views, not additional usage. Failed calls without a response/usage ID must remain separate attempt/error records with unavailable usage, not fabricated records under this final-snapshot schema.

This schema is a preparation draft addressing Gemma's broker review. It has not yet been cross-reviewed or integrated into a qualified broker. It does not replace raw controller events or provide final session ancestry, timing, endpoint freezing or native-step correlation. Existing immutable review reports remain unchanged.
