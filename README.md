# Workboard Lab — construction baseline

Local disposable fixture only. Not production-ready or qualified for subjects. This revision needs different-model cross-review, trusted verification and clean-environment qualification.

## Fresh setup

Use Node 24.19.0 and npm 10.9.0, Linux x64. From this directory:

```sh
npm ci
npx playwright install chromium
npm run build
npm run typecheck
npm run lint
npm test
npm run e2e
npm run reset
npm start
```

Open http://localhost:3000. `npm run e2e` builds, resets `data/e2e.sqlite`, and starts its own server on port 3101; it fails rather than reusing a listener. Chromium requires its OS libraries (on supported machines, `npx playwright install-deps chromium` may require administrator privileges). No external service is required at runtime. To run Vite's dev server in a separate terminal, `npx vite --host 127.0.0.1` proxies `/api` to the running API on port 3000; set `BETTER_AUTH_URL=http://localhost:5173` for that same-origin browser. Build and start serves the SPA and API from the Node server instead.

Reset **deletes** the selected disposable SQLite file and its WAL/SHM, initializes Better Auth tables via its migration API, and seeds the specification's three users/workspaces/items. Stop the server before reset. Only files in this project's `data` directory are allowed; `WORKBOARD_DB` is a filename ending `.sqlite`, not a path. Defaults to `workboard.sqlite`; tests use dedicated filenames. The directory and database may not be symlinks. `PORT` defaults to 3000; `BETTER_AUTH_URL` defaults to `http://localhost:3000` and must match the browser origin, including port. `BETTER_AUTH_SECRET` defaults to a public disposable-only value; never use this fixture or its credentials for real data. Setting it to another value invalidates existing cookies. `npm start` requires the database already reset and the SPA already built.

Seed logins: `ada@workboard.test` / `ada-passphrase-01`; `bruno@workboard.test` / `bruno-passphrase-02`; `cleo@workboard.test` / `cleo-passphrase-03`.

`npm test` is unit plus real loopback HTTP API/SQLite tests; it resets `data/api-test.sqlite`. `npm run e2e` includes real browser auth and uses a second SQLite connection for persistence assertions. Both mutate only their dedicated local fixture databases. They should not be run concurrently with another process using the same test filename or port. Tests are representative, not a task acceptance suite. Source bindings, observations, author record, exact command outcomes and hashes are outside the app directory in `/workspace/output/`.
