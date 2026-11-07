import { describe, expect, it } from "vitest";
import { compareItemsForList } from "../../shared/domain.js";

describe("compareItemsForList", () => {
  it("orders by updatedAt descending", () => {
    const a = { updatedAt: "2026-11-04T09:00:00.000Z", id: "wi_a" };
    const b = { updatedAt: "2026-11-04T10:00:00.000Z", id: "wi_b" };
    expect(compareItemsForList(a, b)).toBeGreaterThan(0);
    expect(compareItemsForList(b, a)).toBeLessThan(0);
  });

  it("breaks ties by id ascending for stable pagination later", () => {
    const a = { updatedAt: "2026-11-04T09:00:00.000Z", id: "wi_002" };
    const b = { updatedAt: "2026-11-04T09:00:00.000Z", id: "wi_010" };
    expect(compareItemsForList(a, b)).toBeLessThan(0);
    expect(compareItemsForList(b, a)).toBeGreaterThan(0);
    expect(compareItemsForList(a, { ...a })).toBe(0);
  });

  it("sorts a mixed list deterministically", () => {
    const list = [
      { updatedAt: "2026-11-01T00:00:00.000Z", id: "wi_b" },
      { updatedAt: "2026-11-03T00:00:00.000Z", id: "wi_d" },
      { updatedAt: "2026-11-03T00:00:00.000Z", id: "wi_a" },
    ];
    const sorted = [...list].sort(compareItemsForList);
    expect(sorted.map((i) => i.id)).toEqual(["wi_a", "wi_d", "wi_b"]);
  });
});
