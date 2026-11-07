import { Hono } from "hono";
import { getMigrations } from "better-auth/db/migration";
import { migrate, openDatabase, type SqliteDb } from "./db.js";
import { buildAuth, type Auth, type AuthOptions } from "./auth.js";
import { registerApiRoutes } from "./api.js";
import { jsonError, RouteError } from "./errors.js";
import { APP_NAME, nowIso } from "../shared/domain.js";

export interface AppHandle {
  app: Hono;
  auth: Auth;
  db: SqliteDb;
}

/**
 * Build the full Hono app (API + Better Auth) on top of a SQLite connection.
 * Used by server/main.ts, the reset script and the API integration tests.
 *
 * Better Auth 1.7.18 does not auto-create its tables: we run its own
 * migration program (`getMigrations` + `runMigrations`) on every boot. The
 * migration is idempotent (no-op once the tables exist).
 */
export async function buildApp(
  db: SqliteDb,
  opts: AuthOptions = {}
): Promise<AppHandle> {
  migrate(db);
  const auth = buildAuth(db, opts);
  const mg = await getMigrations(auth.options);
  await mg.runMigrations();

  const app = new Hono();

  registerApiRoutes(app, { db, auth });

  app.onError((err, c) => {
    if (err instanceof RouteError) {
      return jsonError(c, err.status, err.code, err.message, err.fields);
    }
    console.error("[workboard] unhandled error:", err);
    return jsonError(c, 500, "internal_error", `${APP_NAME} internal error.`);
  });

  app.notFound((c) =>
    jsonError(c, 404, "not_found", "Unknown API endpoint.")
  );

  return { app, auth, db };
}

/** Convenience for scripts/tests: open + build in one call. */
export async function buildAppFromFile(dbFile: string, opts: AuthOptions = {}): Promise<AppHandle> {
  const db = openDatabase(dbFile);
  return buildApp(db, opts);
}

export { nowIso };
