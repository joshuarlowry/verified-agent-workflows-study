# PREPARATION_PROVENANCE — GLM R1 documentation-corpus cross-review

**Reviewer / session.** GLM (`z-ai/glm-5.3-flash`, Relace FP4), fresh documentation cross-review
session ("glm-docs-cross-review" continuation for revision R1). No other model or subagent was
invoked. No controller measurements, provider-side routing evidence, or wall-clock truth are
available in this endpoint; nothing here asserts otherwise. Cross-review is the registered method
(different authorized study model, fresh session); it is **not** independent-model-family
qualification and no self-approval of any artifact is claimed.

**Inputs (immutable; never modified).** `/workspace/inputs/` exactly as supplied:

| Input | SHA-256 |
|---|---|
| `corpus/CORPUS_BUILD_PROVENANCE_R1.md` | `17968d4549903607d49fda29b40ccd8aa8ed16bfe8bae2ca9a58b68042d0e0cf` |
| `corpus/CORPUS_MANIFEST.json` | `b4a9c538fad64801107f11f9efd9993b25a6f0e162aaa784e50f4b81ca4746bf` |
| `corpus/SERVE_COMMAND.sh` | `ee4cf30cfdff44aeca34257adafabd2c0de30f4bf91f6b7c508ec06ff816b429` |
| `corpus/SOURCE_SELECTION_OMISSIONS.md` | `bd0ffb370385b515b080923d43a6393c0116cab839094a00db5fbccb271029aa` |
| `corpus/SHA256SUMS` | `ee10b86ba78a2e5ea227985183d3ac89379fb7186af39c8710a7b92a54b04c07` |
| `registration.json` | `017aac59974b26caffeaed6dd04c911072145bca2c5fe286187bedfe1cd66844` |
| `application-package-lock.json` | `2fa59272fde383011374d769e06b419946b197aedf42887b7d6860faee471246` |
| `prior-review.json` | `d617e57ecabced0d4f28be4839e9f9ef77305cfcccf6368eef8fd3445306e3ca` |

**Environment actually used.** Linux; node v24.19.0, npm 10.9.0; pinned `@neuledge/context` 1.3.3
read from the mounted `/tools/context/node_modules` (cli.js `550c2472…08bf45`, package.json
`7f61f40b…335` — both re-hashed and matching `CORPUS_MANIFEST.json#/context`). Reviewer-private
`~/.context/packages` received fresh `cp` copies of the 22 approved archives; `context list`
reports 22 packages / 167 sections. The endpoint's network was reachable, so upstream refs were
independently re-resolved and a 10-file sample re-fetched byte-identically; a true network-disabled
container test was **not** possible here (`unshare -n` denied) and was approximated only by a
proxy-blackhole scoped-serve check.

**What was verified (all exit codes recorded in `/workspace/diagnostics/`).**

1. `sha256sum -c SHA256SUMS` — 356/356 OK, exit 0; all 355 manifest `files` hashes re-hashed
   independently; disk inventory == manifest set (no orphans/missing).
2. Independent equivalence (`glm_equivalence_check.py`): 22 archives, 118 files reconstructed
   byte-for-byte from 167 chunks; chunk-id sets equal; `PRAGMA integrity_check` ok on all; FTS5
   `integrity-check` passes on scratch copies; fts5vocab doc set == chunks ids. Builder's own
   `equivalence.py` re-run from fresh copies: ok, mapping sets identical to the preserved result.
3. Scoped serve via stdio MCP (`glm_serve_probe.mjs`): `tools/list` == `get_docs` only; enum set ==
   exactly the 22 approved identities; unlisted / wrong-version / bare / padded / traversal / empty
   library arguments all rejected with `MCP error -32602`; unscoped serve exposes
   `search_packages` + `download_package`. Builder's `serve_probe.py` re-run from fresh copies:
   ok, and regenerates `SERVE_COMMAND.sh` byte-identically.
4. Retrieval: 47/47 preserved queries pass on independent rerun (expected source file **and**
   expected API token in returned content); nonsense-term control empty; the five empty-topic
   queries from the first review now return content (WAL content lives under `sqlite@3.53.4`).
   `context query` exit codes are not emptiness signals; JSON results arrays were used.
5. Sources/versions: all 18 repository refs re-resolved identically at review time (13 exact tags,
   5 moving refs); 92/92 raw files match recorded SHA-256; 10/10 sampled files re-fetched
   byte-identical; all 118 `selection.json` `source_sha256` verified against `raw/`; 102 verbatim
   line-range entries reproduce exactly from `raw[line_start..line_end]` with only the declared
   two-heading wrapper; 4 installed-declaration entries verified fenced; 16 Turndown conversions
   verified by raw hash + content spot checks (converter not re-run); 4 installed-package
   evidence entries cross-verified against the actual lockfile (versions, sha512 integrity, MIT).
6. Licenses: 25 evidence files verified present and matching claimed types (17 MIT detections
   incl. packages, Apache-2.0, CC-BY-4.0 ×2, CC-BY-SA-2.5 full text, W3C SWD 2023 + full terms,
   SQLite public-domain statement). No license text is indexed as technical content.
7. Hint scan: 118 files + 167 stored chunks scanned for task/app/ID/contract/acceptance/fixture
   terms — only 10 generic upstream ESLint `fixtures` examples; negative otherwise. No task
   contracts or reference solutions exist in this endpoint, so this cannot rule out invisible hints.
8. SQLite engine: better-sqlite3@13.0.3 from the build's disposable install (package-lock
   byte-identical to `application-package-lock.json`) returns `sqlite_version()` = 3.53.4.
9. Prior-review dispositions: 16 of 19 resolved by R1's rebuild or recorded as resolved-with-open
   coordinator actions; 2 remain open coordinator-side (stale `registration.json` corpus sections,
   stale `source-inventory.json`); 1 not applicable. Details and evidence in
   `/workspace/DOCS_R1_CROSS_REVIEW.json#/original_finding_dispositions`.

**Honest gaps / non-approvals.** Publication of technical extracts, archives, raw downloads and
logs remains **withheld**: MDN contributor attribution (CC-BY-SA-2.5 + share-alike), W3C
derivative-section copyright review, CC attribution preparation (react.dev, TypeScript-Website),
SQLite public-domain caveats and Node third-party notices are captured as evidence but their
completeness is unreviewed; no legal guarantee is offered, and qualified retrieval/use is a
different assessment from public copying. 75 of 76 manifest input hashes are unverifiable here
(baseline/first-corpus/source-inventory not supplied); the builder session's
`inputs/registration.json` (`c43765d1…`) differs from this endpoint's registration revision
(`017aac59…`) as the provenance itself discloses. The preserved `verify_manifest.py` resolves
input paths against the builder session's layout and cannot pass its input section in this
endpoint's layout — a minor tooling portability defect for the coordinator. The real
network-disabled OpenCode/role integration has **not** been performed and is **not** approved by
standalone retrieval tests; only progression *to* that qualification is recommended.

**Outputs (reviewer-authored, unapproved).** `/workspace/DOCS_R1_CROSS_REVIEW.json` (this review's
verdicts, dispositions, exact hashes, reproductions, gaps, progression decision) and
`/workspace/PREPARATION_PROVENANCE.md` (this file), plus all scripts/logs under
`/workspace/diagnostics/`. Fresh working copies for re-running preserved diagnostics live at
`/workspace/diagnostics/fresh/` and `/workspace/diagnostics/fresh2/`. Nothing under
`/workspace/inputs/` was written, and no app, tests, replacement corpus, production change,
deploy/push/merge, or study dispatch occurred.
