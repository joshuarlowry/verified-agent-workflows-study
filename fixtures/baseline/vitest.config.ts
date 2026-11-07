import { defineConfig } from "vitest/config";

// Unit/domain and API (integration) tests run in Node with real SQLite files.
export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/unit/**/*.test.ts", "tests/api/**/*.test.ts"],
    testTimeout: 20_000,
    hookTimeout: 30_000,
    pool: "forks",
    reporters: ["default"],
  },
});
