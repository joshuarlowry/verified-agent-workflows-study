# Preparation cross-review provenance

- **Phase:** cross-review only, not calibration, study collection, reference implementation or sealed-test authoring. Review-time clock observation: `2026-11-07T03:54:47+00:00` from the workspace shell; no completion timestamp is asserted.
- **Reviewer:** Terra Azure High (`study2-terra-fixture-review/terra`); requested `openai/gpt-6.1-terra`, high reasoning, OpenCode/LiteLLM/OpenRouter/Azure route. The actual provider and resolved revision of this session were not independently observed. The registered prior resolved revision is not evidence of this session's revision. No other model or subagent was invoked.
- **Disclosure:** The user authorized Gemma, GLM and Terra to construct and cross-review fixtures in separate sessions. That does **not** establish authorship independent of the evaluated model families. Cross-review is substantive evidence, not independent-family qualification.

## Reviewed inputs

- GLM-authored immutable `inputs/fixture/`: baseline application, tests, contract, 4 calibration and 15 scored drafts, FAQ, source inventory and builder provenance. `inputs/builder-first-endpoint.json` SHA-256 `5cb0388dbd10cc348f9140af986ae7f748fd59c08510cb020ed72ee1ae1f34fa`; all 68 listed path hashes and sizes matched, with no extra fixture files. Its declared tree hash is `1f0b63fae9392282474183f4015bf3599c5a32c6d9bbc1c39d65a9e895e72ad3`; its aggregate encoding was not given. Independently computed fixture tree SHA-256 `cd25e6e35a5f2a81952e1bdf0a53ce4c5c6dbc0467f84eb830011cbab4eee142` using the exact algorithm documented in `FIXTURE_CROSS_REVIEW.json`.
- Coordinator-authored `inputs/normalize_usage.py` SHA-256 `9f20bdd0e8c3648e28dab7898d97f71737ca63bfb794defb81d22fcf0d3a2b27`, `inputs/schemas/provider-usage-record.schema.json` SHA-256 `efdfe944f00eec34db9c73abbe0ca633316b3619693f352f63238cbd0e4d3914`, and `inputs/schemas/README.md` SHA-256 `acccade1093196a81c5f0e2f321eaf802b14d5a5633567845e8cce4f00768a28`. Registration context SHA-256 `d14550012c118a997f5bd7d9abb28f53f038b9a08d6b2503b4dda1b4243d8fc6`. No input was edited.

## New review artifacts and scratch

- `FIXTURE_CROSS_REVIEW.json` and this file are authored by this review session. They report defects and boundaries, not authoritative study checks.
- `check-copy/` is a scratch copy of the baseline, with locally installed packages, Playwright browser, generated outputs and disposable SQLite files. Its tracked baseline source and tests matched the input manifest after diagnostics were moved out; it is not a repaired baseline. The first full check failed for a missing browser; after installation, the clean full check passed: 11 unit, 33 API and 16 e2e tests. Exact commands, exit codes and limitations are in the JSON.
- `diagnostics/review-diagnostic.mts` (SHA-256 `0d7f31bb099adbe1aa8212bd04156d4abd1858b3e7cf3923d602c19229492788`) and `diagnostics/usage_probe.py` (SHA-256 `e8b2418eb0d64ba35d21f98a27f9b2b8deb4dbff74c821006b14c59d20f7468d`) were authored solely for this review. The former was briefly inside the scratch copy, causing one lint warning in an intermediate successful check; it was then moved out and the clean full check rerun. They are not sealed tests, reference solutions, task implementations or part of the original artifact.

## Endpoint

Stop here. The JSON prioritizes concrete repairs and records what may proceed to later, separate reference/evaluator authoring. Missing references and sealed tests are expected at this stage, not new defects. Broker/capture qualification and study collection have not begun in this review.
