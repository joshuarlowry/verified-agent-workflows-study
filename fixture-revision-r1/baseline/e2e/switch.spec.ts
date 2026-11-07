import { expect, test } from "@playwright/test";
import { BRUNO_EMAIL, BRUNO_PASSWORD, signIn } from "./helpers.js";

/**
 * Public regression coverage for workspace-switch loading (baseline
 * contract §6): the previously selected workspace's items are never
 * rendered under a newly selected workspace — not while the next load is
 * delayed, and not when it fails. Bruno is the seeded dual-workspace user.
 */

const BOREALIS_ITEMS = "**/api/workspaces/ws_borealis/items";
const APOLLO_HEADING = "Prepare demo script";
const BOREALIS_HEADING = "Rotate API keys";

test.describe("workspace switch clears the previous workspace's items", () => {
  test.beforeEach(async ({ page }) => {
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    await expect(
      page
        .getByRole("list", { name: "Work items" })
        .getByRole("heading", { name: APOLLO_HEADING })
    ).toBeVisible();
  });

  test("a delayed switch shows the loading state, never the old workspace's items", async ({
    page,
  }) => {
    let release: () => void = () => {};
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route(BOREALIS_ITEMS, async (route) => {
      const response = await route.fetch();
      await gate;
      await route.fulfill({ response });
    });

    await page.getByLabel("Workspace", { exact: true }).selectOption({ label: "Borealis Ops" });

    // While the Borealis load is held back, the list must not show Apollo
    // items and must expose the loading state instead.
    const list = page.getByRole("list", { name: "Work items" });
    await expect(list).toHaveCount(1); // present but empty: no stale rows
    await expect(list.getByRole("heading", { name: APOLLO_HEADING })).toHaveCount(0);
    await expect(page.getByText("Loading work items…")).toBeVisible();
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toHaveCount(0);

    // Releasing the held response completes the switch.
    release();
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toBeVisible();
    await expect(list.getByRole("heading", { name: APOLLO_HEADING })).toHaveCount(0);
  });

  test("a failed switch clears the old workspace's items and Retry recovers", async ({
    page,
  }) => {
    await page.route(BOREALIS_ITEMS, (route) => route.abort());

    await page.getByLabel("Workspace", { exact: true }).selectOption({ label: "Borealis Ops" });

    // The failed load must not resurrect Apollo's items under Borealis.
    const list = page.getByRole("list", { name: "Work items" });
    await expect(page.getByRole("alert").last()).toBeVisible();
    await expect(page.getByRole("button", { name: "Retry" })).toBeVisible();
    await expect(list.getByRole("heading", { name: APOLLO_HEADING })).toHaveCount(0);

    // Remove the fault and recover through the exposed Retry control.
    await page.unroute(BOREALIS_ITEMS);
    await page.getByRole("button", { name: "Retry" }).click();
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
  });
});
