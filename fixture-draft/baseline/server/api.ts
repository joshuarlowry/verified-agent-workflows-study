import type { Hono } from "hono";
import type { Context } from "hono";
import { nowIso, isWorkItemStatus, isValidDueDateFormat, isValidTitle, newId } from "../shared/domain.js";
import type { SessionUser, WorkspaceSummary, WorkItem } from "../shared/types.js";
import { RouteError } from "./errors.js";
import type { SqliteDb } from "./db.js";
import type { Auth } from "./auth.js";

export interface ApiDeps {
  db: SqliteDb;
  auth: Auth;
}

interface WorkspaceRow {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

interface WorkspaceMemberRow extends WorkspaceRow {
  role: string;
}

interface WorkItemRow {
  id: string;
  workspace_id: string;
  title: string;
  notes: string;
  status: string;
  due_date: string | null;
  version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

function workspaceToSummary(row: WorkspaceMemberRow): WorkspaceSummary {
  return {
    id: row.id,
    name: row.name,
    role: row.role as WorkspaceSummary["role"],
    createdAt: row.created_at,
  };
}

function itemToWorkItem(row: WorkItemRow): WorkItem {
  return {
    id: row.id,
    workspaceId: row.workspace_id,
    title: row.title,
    notes: row.notes,
    status: row.status as WorkItem["status"],
    dueDate: row.due_date,
    version: row.version,
    createdBy: row.created_by,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

async function getSessionUser(deps: ApiDeps, c: Context): Promise<SessionUser | null> {
  const session = await deps.auth.api.getSession({ headers: c.req.raw.headers });
  if (!session?.user) {
    return null;
  }
  return { id: session.user.id, email: session.user.email, name: session.user.name };
}

async function requireUser(deps: ApiDeps, c: Context): Promise<SessionUser> {
  const user = await getSessionUser(deps, c);
  if (!user) {
    throw new RouteError(401, "unauthenticated", "Sign in required for this endpoint.");
  }
  return user;
}

interface Membership {
  user: SessionUser;
  role: string;
}

/**
 * Membership gate. Unknown workspace AND non-member both yield 404 so the
 * API does not leak workspace existence to non-members (baseline rule).
 */
function requireMembership(deps: ApiDeps, user: SessionUser, workspaceId: string): Membership {
  const row = deps.db
    .prepare(
      `SELECT m.role AS role
         FROM workspace_members m
        WHERE m.workspace_id = ? AND m.user_id = ?`
    )
    .get(workspaceId, user.id) as { role: string } | undefined;
  if (!row) {
    throw new RouteError(404, "not_found", "Workspace not found.");
  }
  return { user, role: row.role };
}

function requireItemMembership(deps: ApiDeps, user: SessionUser, itemId: string): { item: WorkItemRow; role: string } {
  const item = deps.db.prepare(`SELECT * FROM work_items WHERE id = ?`).get(itemId) as
    | WorkItemRow
    | undefined;
  if (!item) {
    throw new RouteError(404, "not_found", "Work item not found.");
  }
  const membership = requireMembership(deps, user, item.workspace_id);
  return { item, role: membership.role };
}

async function readJsonBody(c: Context): Promise<Record<string, unknown>> {
  let parsed: unknown;
  try {
    parsed = await c.req.json();
  } catch {
    throw new RouteError(400, "validation_failed", "Request body must be valid JSON.");
  }
  if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new RouteError(400, "validation_failed", "Request body must be a JSON object.");
  }
  return parsed as Record<string, unknown>;
}

interface ItemInputPatch {
  title?: string;
  notes?: string;
  status?: WorkItem["status"];
  dueDate?: string | null;
}

/**
 * Baseline input validation for work items.
 * - title: non-empty string (no trimming, no length cap)
 * - notes: string (optional, default "")
 * - status: one of open | in_progress | done (optional, default "open")
 * - dueDate: null or "YYYY-MM-DD" (format check only)
 * Unknown keys are ignored. Values are stored verbatim (no trimming).
 */
function validateItemInput(
  body: Record<string, unknown>,
  mode: "create" | "update"
): ItemInputPatch {
  const patch: ItemInputPatch = {};
  const fields: Record<string, string> = {};

  if ("title" in body) {
    if (!isValidTitle(body.title)) {
      fields.title = "title must be a non-empty string.";
    } else {
      patch.title = body.title;
    }
  } else if (mode === "create") {
    fields.title = "title is required.";
  }

  if ("notes" in body) {
    if (typeof body.notes !== "string") {
      fields.notes = "notes must be a string.";
    } else {
      patch.notes = body.notes;
    }
  }

  if ("status" in body) {
    if (!isWorkItemStatus(body.status)) {
      fields.status = "status must be one of: open, in_progress, done.";
    } else {
      patch.status = body.status;
    }
  }

  if ("dueDate" in body) {
    if (body.dueDate === null) {
      patch.dueDate = null;
    } else if (!isValidDueDateFormat(body.dueDate)) {
      fields.dueDate = "dueDate must be null or a YYYY-MM-DD string.";
    } else {
      patch.dueDate = body.dueDate;
    }
  }

  if (Object.keys(fields).length > 0) {
    throw new RouteError(400, "validation_failed", "Invalid work item input.", fields);
  }
  if (mode === "update" && Object.keys(patch).length === 0) {
    throw new RouteError(
      400,
      "validation_failed",
      "Provide at least one of: title, notes, status, dueDate."
    );
  }
  return patch;
}

const ITEM_COLUMNS = `id, workspace_id, title, notes, status, due_date, version, created_by, created_at, updated_at`;

export function registerApiRoutes(app: Hono, deps: ApiDeps): void {
  const { db, auth } = deps;

  app.on(["POST", "GET"], "/api/auth/*", (c) => auth.handler(c.req.raw));

  app.get("/api/health", (c) =>
    c.json({
      ok: true,
      name: "workboard-lab",
      schemaVersion: 1,
      time: nowIso(),
    })
  );

  app.get("/api/me", async (c) => {
    const user = await requireUser(deps, c);
    const rows = db
      .prepare(
        `SELECT w.id, w.name, w.created_at, m.role
           FROM workspace_members m
           JOIN workspaces w ON w.id = m.workspace_id
          WHERE m.user_id = ?
          ORDER BY w.name ASC`
      )
      .all(user.id) as WorkspaceMemberRow[];
    return c.json({ user, workspaces: rows.map(workspaceToSummary) });
  });

  app.get("/api/workspaces", async (c) => {
    const user = await requireUser(deps, c);
    const rows = db
      .prepare(
        `SELECT w.id, w.name, w.created_at, m.role
           FROM workspace_members m
           JOIN workspaces w ON w.id = m.workspace_id
          WHERE m.user_id = ?
          ORDER BY w.name ASC`
      )
      .all(user.id) as WorkspaceMemberRow[];
    return c.json(rows.map(workspaceToSummary));
  });

  app.post("/api/workspaces", async (c) => {
    const user = await requireUser(deps, c);
    const body = await readJsonBody(c);
    if (!isValidTitle(body.name)) {
      throw new RouteError(400, "validation_failed", "Invalid workspace input.", {
        name: "name must be a non-empty string.",
      });
    }
    const id = newId("ws");
    const ts = nowIso();
    const create = db.transaction(() => {
      db.prepare(
        `INSERT INTO workspaces (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)`
      ).run(id, body.name, ts, ts);
      db.prepare(
        `INSERT INTO workspace_members (workspace_id, user_id, role, created_at) VALUES (?, ?, 'owner', ?)`
      ).run(id, user.id, ts);
    });
    create();
    const row = db.prepare(`SELECT * FROM workspaces WHERE id = ?`).get(id) as WorkspaceRow;
    return c.json(
      { id: row.id, name: row.name, role: "owner" as const, createdAt: row.created_at, updatedAt: row.updated_at },
      201
    );
  });

  app.get("/api/workspaces/:workspaceId", async (c) => {
    const user = await requireUser(deps, c);
    const workspaceId = c.req.param("workspaceId");
    const membership = requireMembership(deps, user, workspaceId);
    const row = db.prepare(`SELECT * FROM workspaces WHERE id = ?`).get(workspaceId) as
      | WorkspaceRow
      | undefined;
    if (!row) {
      throw new RouteError(404, "not_found", "Workspace not found.");
    }
    return c.json({
      id: row.id,
      name: row.name,
      role: membership.role,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    });
  });

  app.get("/api/workspaces/:workspaceId/items", async (c) => {
    const user = await requireUser(deps, c);
    const workspaceId = c.req.param("workspaceId");
    requireMembership(deps, user, workspaceId);
    const rows = db
      .prepare(
        `SELECT ${ITEM_COLUMNS} FROM work_items
          WHERE workspace_id = ?
          ORDER BY updated_at DESC, id ASC`
      )
      .all(workspaceId) as WorkItemRow[];
    return c.json({ workspaceId, items: rows.map(itemToWorkItem) });
  });

  app.post("/api/workspaces/:workspaceId/items", async (c) => {
    const user = await requireUser(deps, c);
    const workspaceId = c.req.param("workspaceId");
    requireMembership(deps, user, workspaceId);
    const body = await readJsonBody(c);
    const patch = validateItemInput(body, "create");
    const id = newId("wi");
    const ts = nowIso();
    db.prepare(
      `INSERT INTO work_items
         (id, workspace_id, title, notes, status, due_date, version, created_by, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)`
    ).run(
      id,
      workspaceId,
      patch.title ?? "",
      patch.notes ?? "",
      patch.status ?? "open",
      patch.dueDate ?? null,
      user.id,
      ts,
      ts
    );
    const row = db.prepare(`SELECT ${ITEM_COLUMNS} FROM work_items WHERE id = ?`).get(id) as WorkItemRow;
    return c.json(itemToWorkItem(row), 201);
  });

  app.patch("/api/items/:id", async (c) => {
    const user = await requireUser(deps, c);
    const { item } = requireItemMembership(deps, user, c.req.param("id"));
    const body = await readJsonBody(c);
    const patch = validateItemInput(body, "update");
    const ts = nowIso();
    const next = {
      title: patch.title ?? item.title,
      notes: patch.notes ?? item.notes,
      status: patch.status ?? item.status,
      dueDate: "dueDate" in patch ? patch.dueDate : (item.due_date ?? null),
    };
    db.prepare(
      `UPDATE work_items
          SET title = ?, notes = ?, status = ?, due_date = ?, version = version + 1, updated_at = ?
        WHERE id = ?`
    ).run(next.title, next.notes, next.status, next.dueDate, ts, item.id);
    const row = db.prepare(`SELECT ${ITEM_COLUMNS} FROM work_items WHERE id = ?`).get(item.id) as WorkItemRow;
    return c.json(itemToWorkItem(row));
  });

  app.delete("/api/items/:id", async (c) => {
    const user = await requireUser(deps, c);
    const { item } = requireItemMembership(deps, user, c.req.param("id"));
    db.prepare(`DELETE FROM work_items WHERE id = ?`).run(item.id);
    return c.body(null, 204);
  });
}
