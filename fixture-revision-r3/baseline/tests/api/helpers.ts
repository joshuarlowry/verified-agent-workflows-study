import fs from "node:fs";
import path from "node:path";
import { openDatabase, removeDatabaseFiles, type SqliteDb } from "../../server/db.js";
import { buildApp, type AppHandle } from "../../server/app.js";
import { seedDatabase } from "../../server/seed.js";

let counter = 0;

export const TEST_BASE_URL = "http://localhost:8999";
export const TEST_PASSWORD = "test-password-123";

export function makeTempDbFile(label: string): string {
  const dir = path.resolve(".tmp");
  fs.mkdirSync(dir, { recursive: true });
  counter += 1;
  return path.join(dir, `test-${label}-${process.pid}-${counter}.db`);
}

export interface TestApp extends AppHandle {
  dbFile: string;
  request: AppHandle["app"]["request"];
  close: () => void;
}

/** Fresh SQLite file + fully built Hono app for one test file. */
export async function createTestApp(label: string): Promise<TestApp> {
  const dbFile = makeTempDbFile(label);
  const db = openDatabase(dbFile);
  const handle = await buildApp(db, { baseURL: TEST_BASE_URL, trustedOrigins: [TEST_BASE_URL] });
  return {
    ...handle,
    dbFile,
    request: handle.app.request,
    close: () => {
      handle.db.close();
      removeDatabaseFiles(dbFile);
    },
  };
}

/** Extract the better-auth session cookie from a Response for reuse. */
export function sessionCookie(res: Response): string {
  const setCookies =
    typeof res.headers.getSetCookie === "function" ? res.headers.getSetCookie() : [];
  const pairs = setCookies
    .map((cookie) => cookie.split(";")[0] ?? "")
    .filter((pair) => pair.length > 0);
  if (pairs.length === 0) {
    throw new Error("no set-cookie header in auth response");
  }
  return pairs.join("; ");
}

export interface AuthedClient {
  cookie: string;
  userId: string;
}

/** Real sign-up + sign-in over HTTP through the mounted Better Auth handler. */
export async function signUpAndSignIn(
  t: TestApp,
  email: string,
  password = TEST_PASSWORD,
  name = "Test User"
): Promise<AuthedClient> {
  const signUpRes = await t.request("/api/auth/sign-up/email", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  if (signUpRes.status !== 200) {
    throw new Error(`sign-up failed (${signUpRes.status}): ${await signUpRes.text()}`);
  }
  // HTTP sign-up returns `{ token, user }` (Better Auth 1.7.18).
  const user = ((await signUpRes.json()) as { user: { id: string } }).user;

  const signInRes = await t.request("/api/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (signInRes.status !== 200) {
    throw new Error(`sign-in failed (${signInRes.status}): ${await signInRes.text()}`);
  }
  return { cookie: sessionCookie(signInRes), userId: user.id };
}

/** Sign in with an existing (e.g. seeded) account. */
export async function signInOnly(
  t: TestApp,
  email: string,
  password: string
): Promise<AuthedClient> {
  const signInRes = await t.request("/api/auth/sign-in/email", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (signInRes.status !== 200) {
    throw new Error(`sign-in failed (${signInRes.status}): ${await signInRes.text()}`);
  }
  const user = ((await signInRes.json()) as { user: { id: string } }).user;
  return { cookie: sessionCookie(signInRes), userId: user.id };
}

export async function seedDemoData(t: TestApp): Promise<void> {
  await seedDatabase(t.db, t.auth);
}

/** JSON request helper returning parsed body + status. */
export async function call(
  t: TestApp,
  method: "GET" | "POST" | "PATCH" | "DELETE",
  url: string,
  cookie: string | null,
  body?: unknown
): Promise<{ status: number; json: unknown }> {
  const res = await t.request(url, {
    method,
    headers: {
      ...(cookie ? { cookie } : {}),
      ...(body !== undefined ? { "content-type": "application/json" } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) {
    return { status: 204, json: null };
  }
  return { status: res.status, json: (await res.json()) as unknown };
}

export function errCode(json: unknown): string {
  const body = json as { error?: { code?: string } };
  return body.error?.code ?? "<missing code>";
}

export function errFields(json: unknown): Record<string, string> {
  const body = json as { error?: { fields?: Record<string, string> } };
  return body.error?.fields ?? {};
}

export type Db = SqliteDb;
