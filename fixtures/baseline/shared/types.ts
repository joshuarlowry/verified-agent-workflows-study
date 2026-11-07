// Wire types shared between the Hono API and the React UI.
// JSON field names are camelCase (see docs/baseline-contract.md).

import type { WorkItemStatus, WorkspaceRole } from "./domain.js";

export interface SessionUser {
  id: string;
  email: string;
  name: string;
}

export interface WorkspaceSummary {
  id: string;
  name: string;
  role: WorkspaceRole;
  createdAt: string;
}

export interface MeResponse {
  user: SessionUser;
  workspaces: WorkspaceSummary[];
}

export interface WorkspaceDetail {
  id: string;
  name: string;
  role: WorkspaceRole;
  createdAt: string;
  updatedAt: string;
}

export interface WorkItem {
  id: string;
  workspaceId: string;
  title: string;
  notes: string;
  status: WorkItemStatus;
  /** `YYYY-MM-DD` or null. */
  dueDate: string | null;
  version: number;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface ItemListResponse {
  workspaceId: string;
  items: WorkItem[];
}

export interface HealthResponse {
  ok: true;
  name: string;
  schemaVersion: number;
  time: string;
}
