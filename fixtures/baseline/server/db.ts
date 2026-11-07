import fs from "node:fs";
import Database from "better-sqlite3";
import { SCHEMA_VERSION } from "../shared/domain.js";

export type SqliteDb = Database.Database;

/**
 * Open (or create) the SQLite database and apply the idempotent baseline DDL.
 * The same function is used by the server, the reset script and tests.
 */
export function openDatabase(file: string): SqliteDb {
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.pragma("busy_timeout = 5000");
  migrate(db);
  return db;
}

/** Idempotent DDL for the baseline app tables (Better Auth manages its own). */
export function migrate(db: SqliteDb): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS workspaces (
      id          TEXT PRIMARY KEY,
      name        TEXT NOT NULL,
      created_at  TEXT NOT NULL,
      updated_at  TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS workspace_members (
      workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
      user_id      TEXT NOT NULL,
      role         TEXT NOT NULL CHECK (role IN ('owner', 'member')),
      created_at   TEXT NOT NULL,
      PRIMARY KEY (workspace_id, user_id)
    );

    CREATE INDEX IF NOT EXISTS idx_workspace_members_user
      ON workspace_members(user_id);

    CREATE TABLE IF NOT EXISTS work_items (
      id           TEXT PRIMARY KEY,
      workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
      title        TEXT NOT NULL,
      notes        TEXT NOT NULL DEFAULT '',
      status       TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'done')),
      due_date     TEXT,
      version      INTEGER NOT NULL DEFAULT 1,
      created_by   TEXT NOT NULL,
      created_at   TEXT NOT NULL,
      updated_at   TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_work_items_workspace
      ON work_items(workspace_id, updated_at DESC, id ASC);

    CREATE TABLE IF NOT EXISTS meta (
      key   TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );

    INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', '${SCHEMA_VERSION}');
  `);
}

/** Delete a database file plus its WAL/SHM sidecars. */
export function removeDatabaseFiles(file: string): void {
  for (const suffix of ["", "-wal", "-shm"]) {
    fs.rmSync(`${file}${suffix}`, { force: true });
  }
}
