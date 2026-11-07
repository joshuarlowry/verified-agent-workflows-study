import { describe, expect, it } from "vitest";
import { newId, nowIso } from "../../shared/domain.js";

describe("newId", () => {
  it("produces prefixed opaque ids", () => {
    const ws = newId("ws");
    const wi = newId("wi");
    expect(ws).toMatch(/^ws_[0-9a-f]{20}$/);
    expect(wi).toMatch(/^wi_[0-9a-f]{20}$/);
  });

  it("is unique across calls", () => {
    const seen = new Set(Array.from({ length: 200 }, () => newId("wi")));
    expect(seen.size).toBe(200);
  });
});

describe("nowIso", () => {
  it("returns ISO-8601 UTC strings", () => {
    const value = nowIso();
    expect(value).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    expect(new Date(value).toISOString()).toBe(value);
  });
});
