import { describe, expect, it } from "vitest";
import {
  STATUS_LABELS,
  WORK_ITEM_STATUSES,
  isWorkItemStatus,
  isValidDueDateFormat,
  isValidTitle,
  isWorkspaceRole,
} from "../../shared/domain.js";

describe("work item statuses", () => {
  it("exposes exactly the three baseline statuses with labels", () => {
    expect([...WORK_ITEM_STATUSES]).toEqual(["open", "in_progress", "done"]);
    expect(STATUS_LABELS.open).toBe("Open");
    expect(STATUS_LABELS.in_progress).toBe("In progress");
    expect(STATUS_LABELS.done).toBe("Done");
  });

  it("accepts only known statuses", () => {
    expect(isWorkItemStatus("open")).toBe(true);
    expect(isWorkItemStatus("in_progress")).toBe(true);
    expect(isWorkItemStatus("done")).toBe(true);
    expect(isWorkItemStatus("archived")).toBe(false);
    expect(isWorkItemStatus("OPEN")).toBe(false);
    expect(isWorkItemStatus("")).toBe(false);
    expect(isWorkItemStatus(null)).toBe(false);
    expect(isWorkItemStatus(42)).toBe(false);
  });

  it("accepts only known workspace roles", () => {
    expect(isWorkspaceRole("owner")).toBe(true);
    expect(isWorkspaceRole("member")).toBe(true);
    expect(isWorkspaceRole("admin")).toBe(false);
  });
});

describe("baseline title validation", () => {
  it("requires a non-empty string and does not trim", () => {
    expect(isValidTitle("Launch prep")).toBe(true);
    expect(isValidTitle("   ")).toBe(true); // whitespace-only passes in baseline
    expect(isValidTitle("")).toBe(false);
    expect(isValidTitle(undefined)).toBe(false);
    expect(isValidTitle(7)).toBe(false);
  });
});

describe("baseline due date validation", () => {
  it("accepts YYYY-MM-DD shape only", () => {
    expect(isValidDueDateFormat("2026-11-12")).toBe(true);
    expect(isValidDueDateFormat("2026-1-2")).toBe(false);
    expect(isValidDueDateFormat("12/11/2026")).toBe(false);
    expect(isValidDueDateFormat("")).toBe(false);
    // calendar-invalid but shape-valid dates pass in the baseline:
    expect(isValidDueDateFormat("2026-02-30")).toBe(true);
    expect(isValidDueDateFormat(null)).toBe(false);
  });
});
