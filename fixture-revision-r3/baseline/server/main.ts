import fs from "node:fs";
import path from "node:path";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { openDatabase } from "./db.js";
import { buildApp } from "./app.js";
import { seedDatabase } from "./seed.js";
import { APP_NAME } from "../shared/domain.js";
import { jsonError } from "./errors.js";

async function main(): Promise<void> {
  const dbFile = process.env.WORKBOARD_DB ?? "data/workboard.db";
  // 8787 is occupied by the study sandbox harness in this environment; 4310 is a quiet default.
  const port = Number(process.env.WORKBOARD_PORT ?? 4310);
  const serveDist = process.env.WORKBOARD_SERVE_DIST === "1";
  const seed = process.env.WORKBOARD_SEED === "1";
  const baseURL = process.env.WORKBOARD_BASE_URL ?? `http://localhost:${port}`;
  const trustedOrigins = (process.env.WORKBOARD_TRUSTED_ORIGINS ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  // The Vite dev origin is always trusted so `npm run dev` works out of the box.
  for (const devOrigin of ["http://localhost:5173", "http://127.0.0.1:5173"]) {
    if (!trustedOrigins.includes(devOrigin)) {
      trustedOrigins.push(devOrigin);
    }
  }

  fs.mkdirSync(path.dirname(dbFile) || ".", { recursive: true });
  const db = openDatabase(dbFile);
  const { app, auth } = await buildApp(db, { baseURL, trustedOrigins });

  if (seed) {
    const counts = await seedDatabase(db, auth);
    console.log(
      `[workboard] seeded: ${counts.users} users, ${counts.workspaces} workspaces, ${counts.items} items`
    );
  }

  if (serveDist) {
    app.use("*", serveStatic({ root: "./dist" }));
    app.get("*", (c) => {
      if (c.req.path.startsWith("/api")) {
        return jsonError(c, 404, "not_found", "Unknown API endpoint.");
      }
      const indexPath = path.resolve("dist/index.html");
      if (fs.existsSync(indexPath)) {
        return c.html(fs.readFileSync(indexPath, "utf8"));
      }
      return c.text("dist/index.html not found - run `npm run build` first.", 500);
    });
  }

  const server = serve({ fetch: app.fetch, port }, (info) => {
    console.log(`[workboard] ${APP_NAME} listening on http://localhost:${info.port}`);
    console.log(`[workboard] db: ${dbFile}${serveDist ? " (serving dist/)" : ""}`);
  });

  const shutdown = (signal: string) => {
    console.log(`[workboard] received ${signal}, shutting down`);
    server.close(() => {
      db.close();
      process.exit(0);
    });
    setTimeout(() => process.exit(0), 2000).unref();
  };
  process.on("SIGINT", () => shutdown("SIGINT"));
  process.on("SIGTERM", () => shutdown("SIGTERM"));
}

main().catch((err) => {
  console.error("[workboard] fatal:", err);
  process.exit(1);
});
