import Database from "better-sqlite3";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  call,
  createTestApp,
  errCode,
  errFields,
  signUpAndSignIn,
  type AuthedClient,
  type TestApp,
} from "./helpers.js";

let t: TestApp;
let owner: AuthedClient;
let outsider: AuthedClient;
let workspaceId: string;
let itemId: string;

beforeAll(async () => {
  t = await createTestApp("items");
  owner = await signUpAndSignIn(t, "owner@example.test", undefined, "Owner");
  outsider = await signUpAndSignIn(t, "outsider@example.test", undefined, "Outsider");
  const created = (await call(t, "POST", "/api/workspaces", owner.cookie, { name: "Item Lab" }))
    .json as { id: string };
  workspaceId = created.id;
});

afterAll(() => {
  t?.close();
});

describe("item creation", () => {
  it("creates an item with defaults and persists it (verified through a second connection)", async () => {
    const { status, json } = await call(t, "POST", `/api/workspaces/${workspaceId}/items`, owner.cookie, {
      title: "Write baseline tests",
      notes: "They must touch the real database.",
      status: "in_progress",
      dueDate: "2026-11-30",
    });
    expect(status).toBe(201);
    const item = json as {
      id: string;
      title: string;
      notes: string;
      status: string;
      dueDate: string | null;
      version: number;
      createdBy: string;
      workspaceId: string;
    };
    itemId = item.id;
    expect(item.version).toBe(1);
    expect(item.status).toBe("in_progress");
    expect(item.dueDate).toBe("2026-11-30");
    expect(item.createdBy).toBe(owner.userId);
    expect(item.workspaceId).toBe(workspaceId);

    // Open a brand-new connection to prove the row is really on disk (WAL included).
    const fresh = new Database(t.dbFile);
    try {
      const row = fresh
        .prepare("SELECT title, notes, status, due_date, created_by FROM work_items WHERE id = ?")
        .get(itemId) as
        | { title: string; notes: string; status: string; due_date: string; created_by: string }
        | undefined;
      expect(row).toBeDefined();
      expect(row!.title).toBe("Write baseline tests");
      expect(row!.created_by).toBe(owner.userId);
    } finally {
      fresh.close();
    }
  });

  it("applies documented defaults when only a title is given", async () => {
    const { json } = await call(t, "POST", `/api/workspaces/${workspaceId}/items`, owner.cookie, {
      title: "Defaults check",
    });
    const item = json as { status: string; notes: string; dueDate: string | null; version: number };
    expect(item.status).toBe("open");
    expect(item.notes).toBe("");
    expect(item.dueDate).toBeNull();
    expect(item.version).toBe(1);
  });

  it("stores titles verbatim (no trimming in the baseline)", async () => {
    const { json } = await call(t, "POST", `/api/workspaces/${workspaceId}/items`, owner.cookie, {
      title: "  padded title  ",
    });
    expect((json as { title: string }).title).toBe("  padded title  ");
  });

  it("rejects invalid input with per-field messages", async () => {
    const { status, json } = await call(
      t,
      "POST",
      `/api/workspaces/${workspaceId}/items`,
      owner.cookie,
      { title: "", status: "archived", dueDate: "11/30/2026" }
    );
    expect(status).toBe(400);
    expect(errCode(json)).toBe("validation_failed");
    const fields = errFields(json);
    expect(fields.title).toContain("non-empty");
    expect(fields.status).toContain("open, in_progress, done");
    expect(fields.dueDate).toContain("YYYY-MM-DD");
  });

  it("rejects a missing title at creation", async () => {
    const { status, json } = await call(t, "POST", `/api/workspaces/${workspaceId}/items`, owner.cookie, {
      notes: "no title",
    });
    expect(status).toBe(400);
    expect(errFields(json).title).toBeTruthy();
    expect(errCode(json)).toBe("validation_failed");
  });
});

describe("item listing and ownership", () => {
  it("lists items in updated_at DESC order", async () => {
    const { json } = await call(t, "GET", `/api/workspaces/${workspaceId}/items`, owner.cookie);
    const list = (json as { items: { id: string; updatedAt: string }[] }).items;
    expect(list.length).toBeGreaterThanOrEqual(3);
    for (let i = 1; i < list.length; i += 1) {
      const prev = list[i - 1]!;
      const curr = list[i]!;
      expect(prev.updatedAt >= curr.updatedAt || (prev.updatedAt === curr.updatedAt && prev.id < curr.id)).toBe(true);
    }
  });

  it("hides items from non-members with 404", async () => {
    const { status, json } = await call(t, "GET", `/api/workspaces/${workspaceId}/items`, outsider.cookie);
    expect(status).toBe(404);
    expect(errCode(json)).toBe("not_found");
  });

  it("blocks mutations by non-members without changing the database", async () => {
    const before = t.db.prepare("SELECT title, version FROM work_items WHERE id = ?").get(itemId) as {
      title: string;
      version: number;
    };
    const patchRes = await call(t, "PATCH", `/api/items/${itemId}`, outsider.cookie, { title: "Hacked" });
    expect(patchRes.status).toBe(404);
    const deleteRes = await call(t, "DELETE", `/api/items/${itemId}`, outsider.cookie);
    expect(deleteRes.status).toBe(404);
    const after = t.db.prepare("SELECT title, version FROM work_items WHERE id = ?").get(itemId) as {
      title: string;
      version: number;
    };
    expect(after.title).toBe(before.title);
    expect(after.version).toBe(before.version);
  });

  it("404s for unknown item ids", async () => {
    const { status } = await call(t, "PATCH", "/api/items/wi_missing", owner.cookie, { title: "X" });
    expect(status).toBe(404);
  });
});

describe("item updates", () => {
  it("patches fields, bumps version and refreshes updated_at", async () => {
    const before = (await call(t, "GET", `/api/workspaces/${workspaceId}/items`, owner.cookie))
      .json as { items: { id: string; version: number; updatedAt: string }[] };
    const target = before.items.find((i) => i.id === itemId)!;

    const { status, json } = await call(t, "PATCH", `/api/items/${itemId}`, owner.cookie, {
      title: "Renamed via PATCH",
      status: "done",
      dueDate: null,
    });
    expect(status).toBe(200);
    const updated = json as {
      title: string;
      status: string;
      dueDate: string | null;
      version: number;
      updatedAt: string;
      notes: string;
    };
    expect(updated.title).toBe("Renamed via PATCH");
    expect(updated.status).toBe("done");
    expect(updated.dueDate).toBeNull();
    expect(updated.version).toBe(target.version + 1);
    expect(updated.updatedAt > target.updatedAt).toBe(true);
    // untouched fields survive a partial patch
    expect(updated.notes).toBe("They must touch the real database.");
  });

  it("rejects an empty patch body", async () => {
    const { status, json } = await call(t, "PATCH", `/api/items/${itemId}`, owner.cookie, {});
    expect(status).toBe(400);
    expect(errCode(json)).toBe("validation_failed");
  });

  it("rejects invalid field values without touching the row", async () => {
    const before = t.db.prepare("SELECT version FROM work_items WHERE id = ?").get(itemId) as {
      version: number;
    };
    const { status } = await call(t, "PATCH", `/api/items/${itemId}`, owner.cookie, {
      status: "archived",
    });
    expect(status).toBe(400);
    const after = t.db.prepare("SELECT version FROM work_items WHERE id = ?").get(itemId) as {
      version: number;
    };
    expect(after.version).toBe(before.version);
  });
});

describe("item deletion", () => {
  it("deletes and returns 204; the row is gone on a fresh connection", async () => {
    const { status } = await call(t, "DELETE", `/api/items/${itemId}`, owner.cookie);
    expect(status).toBe(204);
    const fresh = new Database(t.dbFile);
    try {
      const row = fresh.prepare("SELECT id FROM work_items WHERE id = ?").get(itemId);
      expect(row).toBeUndefined();
    } finally {
      fresh.close();
    }
    const getRes = await call(t, "PATCH", `/api/items/${itemId}`, owner.cookie, { title: "X" });
    expect(getRes.status).toBe(404);
  });
});

describe("baseline version semantics", () => {
  it("is last-write-wins: patches without a version hint always succeed", async () => {
    const created = (await call(t, "POST", `/api/workspaces/${workspaceId}/items`, owner.cookie, {
      title: "Concurrency baseline",
    })).json as { id: string; version: number };
    const first = await call(t, "PATCH", `/api/items/${created.id}`, owner.cookie, { title: "Edit one" });
    expect(first.status).toBe(200);
    const second = await call(t, "PATCH", `/api/items/${created.id}`, owner.cookie, { title: "Edit two" });
    expect(second.status).toBe(200);
    expect((second.json as { version: number }).version).toBe(created.version + 2);
  });
});
