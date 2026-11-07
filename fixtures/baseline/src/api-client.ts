// Thin JSON fetch wrapper for the Hono API (same origin; cookies included).
export class ApiError extends Error {
  readonly status: number;
  readonly code: string | null;
  readonly fields: Record<string, string> | null;

  constructor(status: number, message: string, code: string | null, fields: Record<string, string> | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

export function readErrorMessage(err: unknown, fallback = "Unexpected error."): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

interface ErrorEnvelope {
  error?: { code?: string; message?: string; fields?: Record<string, string> };
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    credentials: "same-origin",
    headers: init.body ? { "content-type": "application/json" } : undefined,
    ...init,
  });
  if (res.status === 204) {
    return undefined as T;
  }
  let payload: unknown;
  try {
    payload = await res.json();
  } catch {
    payload = null;
  }
  if (!res.ok) {
    const envelope = (payload ?? {}) as ErrorEnvelope;
    throw new ApiError(
      res.status,
      envelope.error?.message ?? `Request failed with status ${res.status}.`,
      envelope.error?.code ?? null,
      envelope.error?.fields ?? null
    );
  }
  return payload as T;
}
