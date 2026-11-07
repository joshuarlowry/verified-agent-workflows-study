import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  TEST_PASSWORD,
  call,
  createTestApp,
  errCode,
  sessionCookie,
  signUpAndSignIn,
  type TestApp,
} from "./helpers.js";

let t: TestApp;

beforeAll(async () => {
  t = await createTestApp("auth");
});

afterAll(() => {
  t?.close();
});

describe("health", () => {
  it("responds 200 without auth", async () => {
    const { status, json } = await call(t, "GET", "/api/health", null);
    expect(status).toBe(200);
    expect(json).toMatchObject({ ok: true, name: "workboard-lab", schemaVersion: 1 });
  });
});

describe("sign-up and sign-in over HTTP", () => {
  it("creates an account and returns a session cookie on sign-in", async () => {
    const res = await t.request("/api/auth/sign-up/email", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        email: "maya@example.test",
        password: TEST_PASSWORD,
        name: "Maya Ortiz",
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { token: string; user: { id: string; email: string } };
    expect(body.user.email).toBe("maya@example.test");
    expect(body.user.id).toBeTruthy();
    expect(body.token).toBeTruthy();

    const signIn = await t.request("/api/auth/sign-in/email", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: "maya@example.test", password: TEST_PASSWORD }),
    });
    expect(signIn.status).toBe(200);
    const cookie = sessionCookie(signIn);
    expect(cookie).toContain("better-auth.session_token=");

    const { status, json } = await call(t, "GET", "/api/me", cookie);
    expect(status).toBe(200);
    expect(json).toMatchObject({ user: { id: body.user.id, email: "maya@example.test" } });
    expect((json as { workspaces: unknown[] }).workspaces).toEqual([]);
  });

  it("rejects a wrong password with an error status", async () => {
    const res = await t.request("/api/auth/sign-in/email", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: "maya@example.test", password: "wrong-password" }),
    });
    expect(res.status).toBe(401);
    // Better Auth routes use Better Auth's native error format, NOT the
    // Workboard envelope (documented in docs/baseline-contract.md §5).
    const body = (await res.json()) as { message?: string; code?: string; error?: unknown };
    expect(body.error).toBeUndefined();
    expect(body.code).toBe("INVALID_EMAIL_OR_PASSWORD");
    expect(typeof body.message).toBe("string");
  });

  it("rejects duplicate sign-up", async () => {
    const res = await t.request("/api/auth/sign-up/email", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        email: "maya@example.test",
        password: TEST_PASSWORD,
        name: "Maya Two",
      }),
    });
    expect(res.status).toBeGreaterThanOrEqual(400);
    expect(res.status).toBeLessThan(500);
  });
});

describe("session enforcement", () => {
  it("returns 401 with the unauthenticated code for protected endpoints", async () => {
    for (const [method, url] of [
      ["GET", "/api/me"],
      ["GET", "/api/workspaces"],
      ["POST", "/api/workspaces"],
      ["GET", "/api/workspaces/ws_x/items"],
    ] as const) {
      const { status, json } = await call(t, method, url, null, method === "POST" ? { name: "X" } : undefined);
      expect(status).toBe(401);
      expect(errCode(json)).toBe("unauthenticated");
    }
  });

  it("invalidates the session after sign-out", async () => {
    const client = await signUpAndSignIn(t, "nils@example.test");
    const signOutRes = await t.request("/api/auth/sign-out", {
      method: "POST",
      headers: { "content-type": "application/json", cookie: client.cookie },
      body: "{}",
    });
    expect(signOutRes.status).toBe(200);
    const { status, json } = await call(t, "GET", "/api/me", client.cookie);
    expect(status).toBe(401);
    expect(errCode(json)).toBe("unauthenticated");
  });
});

describe("unknown endpoints", () => {
  it("returns the documented error envelope", async () => {
    const { status, json } = await call(t, "GET", "/api/definitely-not-here", null);
    expect(status).toBe(404);
    expect(errCode(json)).toBe("not_found");
  });

  it("404s an unsupported method on a known path regardless of session state", async () => {
    // Route resolution precedes authentication (docs/baseline-contract.md §5).
    const { status, json } = await call(t, "DELETE", "/api/health", null);
    expect(status).toBe(404);
    expect(errCode(json)).toBe("not_found");
  });
});
