import { defineConfig, devices } from "@playwright/test";

// Real UI/API/database regression tests.
// The webServer builds the UI, resets+seeds a disposable SQLite DB at
// .tmp/e2e.db, then serves the built SPA and the Hono API on one origin.
const PORT = 4599;

export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npm run e2e:serve",
    url: `http://127.0.0.1:${PORT}/api/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 240_000,
    env: {
      WORKBOARD_DB: ".tmp/e2e.db",
      WORKBOARD_PORT: String(PORT),
      WORKBOARD_SERVE_DIST: "1",
      WORKBOARD_SEED: "1",
      WORKBOARD_BASE_URL: `http://127.0.0.1:${PORT}`,
      WORKBOARD_TRUSTED_ORIGINS: `http://127.0.0.1:${PORT},http://localhost:${PORT}`,
    },
  },
});
