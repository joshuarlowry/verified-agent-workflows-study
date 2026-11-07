// Resets (deletes + recreates + seeds) the disposable SQLite database.
//
//   WORKBOARD_DB=data/workboard.db npm run db:reset          # with seed
//   WORKBOARD_DB=data/workboard.db npm run db:reset -- --no-seed
//
// Destructive by design: it removes the file, its WAL/SHM sidecars and all data.
import fs from "node:fs";
import path from "node:path";
import { openDatabase, removeDatabaseFiles } from "../server/db.js";
import { buildApp } from "../server/app.js";
import { seedDatabase } from "../server/seed.js";

async function reset(): Promise<void> {
  const args = process.argv.slice(2);
  const noSeed = args.includes("--no-seed");
  const dbFile = process.env.WORKBOARD_DB ?? "data/workboard.db";

  removeDatabaseFiles(dbFile);
  fs.mkdirSync(path.dirname(dbFile) || ".", { recursive: true });

  const db = openDatabase(dbFile);
  try {
    const handle = await buildApp(db, {
      baseURL: process.env.WORKBOARD_BASE_URL ?? "http://localhost:4310",
    });
    if (!noSeed) {
      const counts = await seedDatabase(db, handle.auth);
      console.log(
        `[db:reset] seeded ${counts.users} users, ${counts.workspaces} workspaces, ${counts.items} items`
      );
    } else {
      console.log("[db:reset] schema created (no seed)");
    }
  } finally {
    db.close();
  }
  console.log(`[db:reset] ready: ${dbFile}`);
}

reset().catch((err) => {
  console.error("[db:reset] failed:", err);
  process.exit(1);
});
