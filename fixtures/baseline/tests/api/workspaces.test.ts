import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  call,
  createTestApp,
  errCode,
  signUpAndSignIn,
  type AuthedClient,
  type TestApp,
} from "./helpers.js";

let t: TestApp;
let alice: AuthedClient;
let bob: AuthedClient;

beforeAll(async () => {
  t = await createTestApp("workspaces");
  alice = await signUpAndSignIn(t, "alice@example.test", undefined, "Alice");
  bob = await signUpAndSignIn(t, "bob@example.test", undefined, "Bob");
});

afterAll(() => {
  t?.close();
});

describe("workspace creation", () => {
  it("creates a workspace and makes the creator the owner (verified in SQLite)", async () => {
    const { status, json } = await call(t, "POST", "/api/workspaces", alice.cookie, {
      name: "Alice Space",
    });
    expect(status).toBe(201);
    const ws = json as { id: string; name: string; role: string; createdAt: string; updatedAt: string };
    expect(ws.name).toBe("Alice Space");
    expect(ws.role).toBe("owner");

    // Real persistence: read the membership row straight from the database.
    const member = t.db
      .prepare("SELECT role FROM workspace_members WHERE workspace_id = ? AND user_id = ?")
      .get(ws.id, alice.userId) as { role: string } | undefined;
    expect(member?.role).toBe("owner");
  });

  it("rejects invalid names with the validation envelope", async () => {
    for (const name of ["", 7, null]) {
      const { status, json } = await call(t, "POST", "/api/workspaces", alice.cookie, { name });
      expect(status).toBe(400);
      expect(errCode(json)).toBe("validation_failed");
    }
    const { status } = await call(t, "POST", "/api/workspaces", alice.cookie, "not-an-object");
    expect(status).toBe(400);
  });

  it("requires auth", async () => {
    const { status } = await call(t, "POST", "/api/workspaces", null, { name: "X" });
    expect(status).toBe(401);
  });
});

describe("workspace visibility", () => {
  it("lists only my workspaces in name order", async () => {
    await call(t, "POST", "/api/workspaces", alice.cookie, { name: "Zeta Room" });
    await call(t, "POST", "/api/workspaces", alice.cookie, { name: "Alpha Room" });
    const { status, json } = await call(t, "GET", "/api/workspaces", alice.cookie);
    expect(status).toBe(200);
    const list = json as { id: string; name: string; role: string }[];
    expect(list.map((w) => w.name)).toEqual(["Alice Space", "Alpha Room", "Zeta Room"]);
    expect(list.every((w) => w.role === "owner")).toBe(true);
  });

  it("hides other users' workspaces (404, not 403, to avoid leaking existence)", async () => {
    const list = (await call(t, "GET", "/api/workspaces", alice.cookie)).json as { id: string }[];
    const aliceWs = list[0]!.id;
    const { status, json } = await call(t, "GET", `/api/workspaces/${aliceWs}`, bob.cookie);
    expect(status).toBe(404);
    expect(errCode(json)).toBe("not_found");
    const itemsRes = await call(t, "GET", `/api/workspaces/${aliceWs}/items`, bob.cookie);
    expect(itemsRes.status).toBe(404);
  });

  it("returns workspace detail with my role", async () => {
    const list = (await call(t, "GET", "/api/workspaces", alice.cookie)).json as { id: string }[];
    const detail = (await call(t, "GET", `/api/workspaces/${list[0]!.id}`, alice.cookie)).json as {
      id: string;
      role: string;
      name: string;
    };
    expect(detail.role).toBe("owner");
    expect(detail.name).toBe("Alice Space");
  });

  it("404s for unknown workspace ids even for the owner", async () => {
    const { status } = await call(t, "GET", "/api/workspaces/ws_does_not_exist", alice.cookie);
    expect(status).toBe(404);
  });
});
