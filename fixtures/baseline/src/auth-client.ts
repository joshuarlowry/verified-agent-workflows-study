import { createAuthClient } from "better-auth/react";

// Same-origin client: in dev, Vite proxies /api to the Hono server; in the
// built app the SPA and API share one origin.
export const authClient = createAuthClient();

/** Defensive extraction of a human-readable message from client errors. */
export function readAuthErrorMessage(err: unknown, fallback: string): string {
  if (err && typeof err === "object") {
    const obj = err as { message?: unknown; error?: { message?: unknown } | string };
    if (typeof obj.message === "string" && obj.message) return obj.message;
    if (typeof obj.error === "string" && obj.error) return obj.error;
    if (obj.error && typeof obj.error === "object" && typeof obj.error.message === "string") {
      return obj.error.message;
    }
  }
  return fallback;
}
