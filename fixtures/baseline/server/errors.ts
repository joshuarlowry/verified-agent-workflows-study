import type { Context } from "hono";
import type { ContentfulStatusCode } from "hono/utils/http-status";
import type { ApiErrorCode } from "../shared/domain.js";

export interface ApiErrorBody {
  error: {
    code: ApiErrorCode;
    message: string;
    fields?: Record<string, string>;
  };
}

/** Standard baseline error envelope: `{ "error": { code, message, fields? } }`. */
export function jsonError(
  c: Context,
  status: ContentfulStatusCode,
  code: ApiErrorCode,
  message: string,
  fields?: Record<string, string>
): Response {
  const body: ApiErrorBody = { error: { code, message } };
  if (fields) {
    body.error.fields = fields;
  }
  return c.json(body, status);
}

export function notFound(c: Context, message = "Not found"): Response {
  return jsonError(c, 404, "not_found", message);
}

export function unauthenticated(c: Context): Response {
  return jsonError(
    c,
    401,
    "unauthenticated",
    "Sign in required for this endpoint."
  );
}

export function validationFailed(
  c: Context,
  message: string,
  fields?: Record<string, string>
): Response {
  return jsonError(c, 400, "validation_failed", message, fields);
}

/**
 * Thrown by route helpers; caught by app.ts and mapped to the error envelope.
 */
export class RouteError extends Error {
  readonly status: ContentfulStatusCode;
  readonly code: ApiErrorCode;
  readonly fields?: Record<string, string>;

  constructor(
    status: ContentfulStatusCode,
    code: ApiErrorCode,
    message: string,
    fields?: Record<string, string>
  ) {
    super(message);
    this.name = "RouteError";
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}
