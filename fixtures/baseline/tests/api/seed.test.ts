import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { call, createTestApp, seedDemoData, signInOnly, type AuthedClient, type TestApp } from "./helpers.js";
import { SEED_ITEMS, SEED_WORKSPACES } from "../../server/seed.js";

let t: TestApp;
let ada: AuthedClient;
let cleo: AuthedClient;

beforeAll(async () => {
  t = await createTestApp("seed");
  await seedDemoData(t);
  // Seed users already exist; sign in over HTTP (exercises real password hashes).
  ada = await signInOnly(t, "ada@workboard.test", "ada-passphrase-01");
  cleo = await signInOnly(t, "cleo@workboard.test", "cleo-passphrase-03");
});

afterAll(() => {
  t?.close();
});

describe("deterministic seed", () => {
  it("creates the documented workspaces, memberships and items", () => {
    const workspaces = t.db.prepare("SELECT id, name FROM workspaces ORDER BY id").all() as {
      id: string;
      name: string;
    }[];
    expect(workspaces).toEqual([
      { id: "ws_apollo", name: "Apollo Launch" },
      { id: "ws_borealis", name: "Borealis Ops" },
    ]);
    const memberCount = (t.db.prepare("SELECT COUNT(*) AS n FROM workspace_members").get() as { n: number }).n;
    expect(memberCount).toBe(4);
    expect(SEED_ITEMS.length).toBe(13);
  });

  it("pins item timestamps and versions so list order is stable", async () => {
    const { status, json } = await call(t, "GET", "/api/workspaces/ws_apollo/items", ada.cookie);
    expect(status).toBe(200);
    const items = (json as { items: { id: string; updatedAt: string; version: number }[] }).items;
    expect(items.map((i) => i.id)).toEqual([
      "wi_103",
      "wi_106",
      "wi_104",
      "wi_102",
      "wi_107",
      "wi_105",
      "wi_101",
      "wi_108",
    ]);
    expect(items.every((i) => i.version === 1)).toBe(true);
  });

  it("matches the declared seed manifest", async () => {
    const rows = t.db
      .prepare("SELECT id, workspace_id, title, status, due_date FROM work_items ORDER BY id")
      .all() as { id: string; workspace_id: string; title: string; status: string; due_date: string | null }[];
    expect(rows).toHaveLength(SEED_ITEMS.length);
    for (const row of rows) {
      const manifest = SEED_ITEMS.find((i) => i.id === row.id)!;
      expect(row.workspace_id).toBe(manifest.workspaceId);
      expect(row.title).toBe(manifest.title);
      expect(row.status).toBe(manifest.status);
      expect(row.due_date).toBe(manifest.dueDate);
    }
  });

  it("enforces membership on seeded workspaces (Cleo cannot see Apollo)", async () => {
    const res = await call(t, "GET", "/api/workspaces/ws_apollo/items", cleo.cookie);
    expect(res.status).toBe(404);
    const mine = await call(t, "GET", "/api/workspaces", cleo.cookie);
    const names = (mine.json as { name: string }[]).map((w) => w.name);
    expect(names).toEqual(["Borealis Ops"]);
  });

  it("declares every seeded workspace id as existing", () => {
    for (const ws of SEED_WORKSPACES) {
      const row = t.db.prepare("SELECT id FROM workspaces WHERE id = ?").get(ws.id);
      expect(row).toBeDefined();
    }
  });
});
