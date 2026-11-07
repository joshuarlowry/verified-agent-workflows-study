import type { SqliteDb } from "./db.js";
import type { Auth } from "./auth.js";

/**
 * Deterministic seed data. Fixed IDs and pinned ISO timestamps so that list
 * ordering, "overdue" examples and cross-references are stable across resets.
 * User rows are created through Better Auth (random ids, hashed passwords);
 * all other rows use the fixed IDs below. Credentials are PUBLIC test data
 * documented in docs/baseline-contract.md.
 */
export interface SeedUser {
  email: string;
  name: string;
  password: string;
}

export const SEED_USERS: SeedUser[] = [
  { email: "ada@workboard.test", name: "Ada Streams", password: "ada-passphrase-01" },
  { email: "bruno@workboard.test", name: "Bruno Calder", password: "bruno-passphrase-02" },
  { email: "cleo@workboard.test", name: "Cleo Marsh", password: "cleo-passphrase-03" },
];

export interface SeedWorkspace {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export const SEED_WORKSPACES: SeedWorkspace[] = [
  { id: "ws_apollo", name: "Apollo Launch", createdAt: "2026-11-01T09:00:00.000Z", updatedAt: "2026-11-01T09:00:00.000Z" },
  { id: "ws_borealis", name: "Borealis Ops", createdAt: "2026-11-01T09:05:00.000Z", updatedAt: "2026-11-01T09:05:00.000Z" },
];

export interface SeedMembership {
  workspaceId: string;
  email: string;
  role: "owner" | "member";
  createdAt: string;
}

export const SEED_MEMBERSHIPS: SeedMembership[] = [
  { workspaceId: "ws_apollo", email: "ada@workboard.test", role: "owner", createdAt: "2026-11-01T09:00:00.000Z" },
  { workspaceId: "ws_apollo", email: "bruno@workboard.test", role: "member", createdAt: "2026-11-01T09:30:00.000Z" },
  { workspaceId: "ws_borealis", email: "bruno@workboard.test", role: "owner", createdAt: "2026-11-01T09:05:00.000Z" },
  { workspaceId: "ws_borealis", email: "cleo@workboard.test", role: "member", createdAt: "2026-11-01T09:20:00.000Z" },
];

export interface SeedItem {
  id: string;
  workspaceId: string;
  title: string;
  notes: string;
  status: "open" | "in_progress" | "done";
  dueDate: string | null;
  createdByEmail: string;
  createdAt: string;
  updatedAt: string;
}

export const SEED_ITEMS: SeedItem[] = [
  // Apollo Launch - listed in updated_at DESC order by the API.
  { id: "wi_103", workspaceId: "ws_apollo", title: "Prepare demo script", notes: "Cover SSO, import and export.", status: "open", dueDate: null, createdByEmail: "ada@workboard.test", createdAt: "2026-11-01T11:00:00.000Z", updatedAt: "2026-11-04T10:15:00.000Z" },
  { id: "wi_106", workspaceId: "ws_apollo", title: "Fix mobile nav overflow", notes: "", status: "in_progress", dueDate: null, createdByEmail: "ada@workboard.test", createdAt: "2026-11-01T11:30:00.000Z", updatedAt: "2026-11-04T09:00:00.000Z" },
  { id: "wi_104", workspaceId: "ws_apollo", title: "Ship onboarding email", notes: "Three-part drip.", status: "done", dueDate: null, createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T10:30:00.000Z", updatedAt: "2026-11-03T16:40:00.000Z" },
  { id: "wi_102", workspaceId: "ws_apollo", title: "Review pricing copy", notes: "Marketing owns final wording.", status: "in_progress", dueDate: "2026-11-05", createdByEmail: "ada@workboard.test", createdAt: "2026-11-01T10:00:00.000Z", updatedAt: "2026-11-03T11:30:00.000Z" },
  { id: "wi_107", workspaceId: "ws_apollo", title: "Write release notes", notes: "", status: "open", dueDate: "2026-11-20", createdByEmail: "ada@workboard.test", createdAt: "2026-11-01T10:15:00.000Z", updatedAt: "2026-11-02T15:05:00.000Z" },
  { id: "wi_105", workspaceId: "ws_apollo", title: "Audit analytics events", notes: "", status: "open", dueDate: "2026-12-01", createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T10:45:00.000Z", updatedAt: "2026-11-02T10:00:00.000Z" },
  { id: "wi_101", workspaceId: "ws_apollo", title: "Draft launch checklist", notes: "Owner: Ada.", status: "open", dueDate: "2026-11-12", createdByEmail: "ada@workboard.test", createdAt: "2026-11-01T09:10:00.000Z", updatedAt: "2026-11-01T14:20:00.000Z" },
  { id: "wi_108", workspaceId: "ws_apollo", title: "Archive old assets", notes: "", status: "done", dueDate: null, createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T09:20:00.000Z", updatedAt: "2026-11-01T09:30:00.000Z" },
  // Borealis Ops
  { id: "wi_202", workspaceId: "ws_borealis", title: "Update status page template", notes: "", status: "in_progress", dueDate: null, createdByEmail: "cleo@workboard.test", createdAt: "2026-11-01T09:40:00.000Z", updatedAt: "2026-11-04T08:45:00.000Z" },
  { id: "wi_205", workspaceId: "ws_borealis", title: "Draft vendor renewal memo", notes: "", status: "open", dueDate: "2026-11-28", createdByEmail: "cleo@workboard.test", createdAt: "2026-11-01T09:50:00.000Z", updatedAt: "2026-11-03T13:10:00.000Z" },
  { id: "wi_201", workspaceId: "ws_borealis", title: "Rotate API keys", notes: "Coordinate with vendors first.", status: "open", dueDate: "2026-11-15", createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T09:12:00.000Z", updatedAt: "2026-11-02T09:15:00.000Z" },
  { id: "wi_203", workspaceId: "ws_borealis", title: "Quarterly access review", notes: "", status: "open", dueDate: null, createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T09:15:00.000Z", updatedAt: "2026-11-01T16:00:00.000Z" },
  { id: "wi_204", workspaceId: "ws_borealis", title: "Patch VPN gateway", notes: "", status: "done", dueDate: null, createdByEmail: "bruno@workboard.test", createdAt: "2026-11-01T09:18:00.000Z", updatedAt: "2026-11-01T10:45:00.000Z" },
];

export interface SeedResult {
  users: number;
  workspaces: number;
  items: number;
}

/**
 * Idempotent seed. Safe to run on an already-seeded database: existing rows
 * (matched by fixed ID / email) are left untouched.
 */
export async function seedDatabase(db: SqliteDb, auth: Auth): Promise<SeedResult> {
  for (const user of SEED_USERS) {
    const exists = db.prepare(`SELECT id FROM user WHERE email = ?`).get(user.email);
    if (!exists) {
      await auth.api.signUpEmail({
        body: { name: user.name, email: user.email, password: user.password },
      });
    }
  }

  const userIdByEmail = new Map<string, string>();
  for (const user of SEED_USERS) {
    const row = db.prepare(`SELECT id FROM user WHERE email = ?`).get(user.email) as
      | { id: string }
      | undefined;
    if (!row) {
      throw new Error(`seed: user ${user.email} missing after sign-up`);
    }
    userIdByEmail.set(user.email, row.id);
  }

  const insertWorkspace = db.prepare(
    `INSERT OR IGNORE INTO workspaces (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)`
  );
  const insertMember = db.prepare(
    `INSERT OR IGNORE INTO workspace_members (workspace_id, user_id, role, created_at) VALUES (?, ?, ?, ?)`
  );
  const insertItem = db.prepare(
    `INSERT OR IGNORE INTO work_items
       (id, workspace_id, title, notes, status, due_date, version, created_by, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)`
  );

  for (const ws of SEED_WORKSPACES) {
    insertWorkspace.run(ws.id, ws.name, ws.createdAt, ws.updatedAt);
  }
  for (const m of SEED_MEMBERSHIPS) {
    const userId = userIdByEmail.get(m.email);
    if (!userId) throw new Error(`seed: no user id for ${m.email}`);
    insertMember.run(m.workspaceId, userId, m.role, m.createdAt);
  }
  for (const item of SEED_ITEMS) {
    const userId = userIdByEmail.get(item.createdByEmail);
    if (!userId) throw new Error(`seed: no user id for ${item.createdByEmail}`);
    insertItem.run(
      item.id,
      item.workspaceId,
      item.title,
      item.notes,
      item.status,
      item.dueDate,
      userId,
      item.createdAt,
      item.updatedAt
    );
  }

  const counts = {
    users: (db.prepare(`SELECT COUNT(*) AS n FROM user`).get() as { n: number }).n,
    workspaces: (db.prepare(`SELECT COUNT(*) AS n FROM workspaces`).get() as { n: number }).n,
    items: (db.prepare(`SELECT COUNT(*) AS n FROM work_items`).get() as { n: number }).n,
  };
  return counts;
}
