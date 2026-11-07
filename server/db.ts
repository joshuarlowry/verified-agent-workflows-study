import Database from 'better-sqlite3';
import { betterAuth } from 'better-auth';
import { getMigrations } from 'better-auth/db/migration';
import { mkdirSync, realpathSync, lstatSync } from 'node:fs';
import { resolve, basename, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

// Only named disposable databases beneath this project's data directory are permitted.
export const dataDir = resolve(dirname(fileURLToPath(import.meta.url)), '../data');
export function dbPath() {
  const name = process.env.WORKBOARD_DB || 'workboard.sqlite';
  if (basename(name) !== name || !/^[a-zA-Z0-9_.-]+\.sqlite$/.test(name)) throw new Error('WORKBOARD_DB must be a local .sqlite filename');
  if (lstatSync(dataDir, { throwIfNoEntry:false }) && realpathSync(dataDir) !== dataDir) throw new Error('data directory must not be a symlink');
  const path = resolve(dataDir, name);
  if (lstatSync(path, { throwIfNoEntry:false })?.isSymbolicLink()) throw new Error('database must not be a symlink');
  return path;
}
export function openDb() {
  mkdirSync(dataDir, { recursive: true });
  const db = new Database(dbPath());
  db.pragma('foreign_keys = ON');
  db.pragma('journal_mode = WAL');
  return db;
}
function authOptions(db: Database.Database) {
  return { database: db, secret: process.env.BETTER_AUTH_SECRET || 'disposable-local-only-secret-1234567890', baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000', emailAndPassword: { enabled: true } };
}
export function makeAuth(db: Database.Database) {
  return betterAuth(authOptions(db));
}
export async function migrate(db: Database.Database) {
  const migration = await getMigrations(authOptions(db));
  await migration.runMigrations();
  db.exec(`CREATE TABLE IF NOT EXISTS workspace (id TEXT PRIMARY KEY, name TEXT NOT NULL, createdAt TEXT NOT NULL, updatedAt TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS membership (workspaceId TEXT NOT NULL REFERENCES workspace(id), userId TEXT NOT NULL REFERENCES user(id), role TEXT NOT NULL CHECK(role IN ('owner','member')), joinedAt TEXT NOT NULL, PRIMARY KEY(workspaceId,userId));
    CREATE TABLE IF NOT EXISTS item (id TEXT PRIMARY KEY, workspaceId TEXT NOT NULL REFERENCES workspace(id), title TEXT NOT NULL, notes TEXT NOT NULL, status TEXT NOT NULL, dueDate TEXT, version INTEGER NOT NULL, createdBy TEXT NOT NULL REFERENCES user(id), createdAt TEXT NOT NULL, updatedAt TEXT NOT NULL);`);
  return makeAuth(db);
}
