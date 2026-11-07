import { betterAuth } from "better-auth";
import type { SqliteDb } from "./db.js";

export interface AuthOptions {
  /** Public base URL of this server, e.g. http://localhost:8787 */
  baseURL?: string;
  /** Extra origins allowed for auth POSTs (e.g. the Vite dev origin). */
  trustedOrigins?: string[];
}

/**
 * Better Auth instance backed directly by our better-sqlite3 connection.
 * Better Auth owns the user/session/account/verification tables and creates
 * them automatically; app tables (workspaces, work_items, ...) live in the
 * same file but are owned by server/db.ts.
 */
export function buildAuth(db: SqliteDb, opts: AuthOptions = {}) {
  return betterAuth({
    database: db,
    emailAndPassword: {
      enabled: true,
      // Baseline defaults: Better Auth's own min length (8) applies.
      // Passwords are seeded/test credentials documented in docs/.
    },
    baseURL: opts.baseURL,
    trustedOrigins: opts.trustedOrigins,
  });
}

export type Auth = ReturnType<typeof buildAuth>;
