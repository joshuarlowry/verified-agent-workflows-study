# CORPUS_BUILD_PROVENANCE.md

## Overview
Construction of a frozen, relevant local documentation corpus for the Workboard Lab baseline. 
The corpus consists of raw Markdown snapshots for system/platform APIs and Context 1.3.3 archives for pinned library dependencies.

## Source Selection Rationale
Sources were selected based on `inputs/source-inventory.json` and observed dependencies in `inputs/baseline/package.json`.
- **System/Platform**: Node.js (v24), SQLite (3.53.4), Browser APIs (Clipboard, Web Storage, History, KeyboardEvent), and WAI-ARIA.
- **Libraries**: Pinned versions of Vite, React, Hono, Better Auth, better-sqlite3, TypeScript, Vitest, Playwright, ESLint, and tsx.

## Construction Process
1. **System Docs**: Fetched via `webfetch` from official MDN/Node/SQLite/W3C sites. Snapshots saved to `docs-files/text/`.
2. **Library Docs**: Built using `node /tools/context/node_modules/@neuledge/context/dist/cli.js add` with `--save context-packages/`.
3. **Manifest**: Generated `CORPUS_MANIFEST.json` with SHA-256 hashes of all artifacts.

## Commands & Exit Codes
- `mkdir -p docs-files/text context-packages`: 0
- `webfetch`: (various) - 0
- `context add`:
  - `vite`: 0
  - `react`: 0
  - `hono`: 0
  - `hono_node_server`: 0
  - `better_auth`: 0
  - `better_sqlite3`: 0
  - `vitest`: 0
  - `playwright`: 0
  - `eslint`: 0
  - `eslint_toolchain`: 0
  - `vitejs_plugin_react`: 0
  - `tsx`: 0
- `sha256sum`: 0

## Limitations & Gaps
- **TypeScript**: Extraction from `typescriptlang.org` failed. Recorded as a gap.
- **@types/better-sqlite3**: Markdown extraction from DefinitelyTyped failed. Recorded as a gap.
- **Version Drift**: Node.js docs are from the latest 24.x line (24.22.2) rather than a 24.19.0-pinned snapshot.
- **Licenses**: Many system documentation pages had unverified license terms; marked as "Not verified".

## Retrieval Smoke Tests
To verify the corpus content and versions, run:
```bash
# Test an archive
node /tools/context/node_modules/@neuledge/context/dist/cli.js query vite 'dev server'

# Test a text file
cat docs-files/text/mdn_clipboard_api_writetext.md
```

## Scoped Serve Command
To serve the approved libraries for a session:
```bash
node /tools/context/node_modules/@neuledge/context/dist/cli.js serve --libs vite react hono better_auth better_sqlite3 vitest playwright eslint tsx
```
