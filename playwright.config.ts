import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir:'tests/e2e', workers:1, fullyParallel:false, timeout:30000,
  use:{ baseURL:'http://localhost:3101', browserName:'chromium', trace:'retain-on-failure' },
  webServer:{ command:'npm run build && npm run reset && npm run start', url:'http://localhost:3101/api/health', reuseExistingServer:false, env:{PORT:'3101',WORKBOARD_DB:'e2e.sqlite',BETTER_AUTH_URL:'http://localhost:3101'}, gracefulShutdown:{signal:'SIGTERM',timeout:3000} }
});
