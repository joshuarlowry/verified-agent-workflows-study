// Pure domain logic shared by the Hono server and the React UI.
// No I/O, no framework imports - everything here must be trivially unit-testable.

export const APP_NAME = "Workboard Lab";
export const SCHEMA_VERSION = 1;

/** The only allowed work-item statuses in the baseline. */
export const WORK_ITEM_STATUSES = ["open", "in_progress", "done"] as const;
export type WorkItemStatus = (typeof WORK_ITEM_STATUSES)[number];

/** Human-readable label for a status, used verbatim by the UI. */
export const STATUS_LABELS: Record<WorkItemStatus, string> = {
  open: "Open",
  in_progress: "In progress",
  done: "Done",
};

export function isWorkItemStatus(value: unknown): value is WorkItemStatus {
  return (
    typeof value === "string" &&
    (WORK_ITEM_STATUSES as readonly string[]).includes(value)
  );
}

export const WORKSPACE_ROLES = ["owner", "member"] as const;
export type WorkspaceRole = (typeof WORKSPACE_ROLES)[number];

export function isWorkspaceRole(value: unknown): value is WorkspaceRole {
  return (
    typeof value === "string" &&
    (WORKSPACE_ROLES as readonly string[]).includes(value)
  );
}

/**
 * Baseline due-date rule: calendar-date shape `YYYY-MM-DD` only.
 * The format is checked; whether it is a real calendar date is NOT validated
 * in the baseline (that is deliberately left for later task variants).
 */
export const DUE_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

export function isValidDueDateFormat(value: unknown): value is string {
  return typeof value === "string" && DUE_DATE_PATTERN.test(value);
}

/** Baseline title rule: a non-empty string. Trimming is NOT applied. */
export function isValidTitle(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

/**
 * List ordering for `GET /api/workspaces/:id/items`:
 * `updated_at` descending, with `id` ascending as a deterministic tiebreak.
 */
export function compareItemsForList(
  a: { updatedAt: string; id: string },
  b: { updatedAt: string; id: string }
): number {
  if (a.updatedAt !== b.updatedAt) {
    return a.updatedAt < b.updatedAt ? 1 : -1;
  }
  return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
}

/** Current time as an ISO-8601 UTC string, e.g. `2026-11-07T12:00:00.000Z`. */
export function nowIso(): string {
  return new Date().toISOString();
}

/** Opaque prefixed identifiers, e.g. `ws_9f1c...` or `wi_...`. */
export function newId(prefix: "ws" | "wi"): string {
  const uuid = globalThis.crypto.randomUUID();
  return `${prefix}_${uuid.replaceAll("-", "").slice(0, 20)}`;
}

/** API error codes used by the baseline. Documented in docs/baseline-contract.md. */
export type ApiErrorCode =
  | "validation_failed"
  | "unauthenticated"
  | "forbidden"
  | "not_found"
  | "conflict"
  | "internal_error";
