import { expect, test } from "@playwright/test";
import { BRUNO_EMAIL, BRUNO_PASSWORD, signIn } from "./helpers.js";

/**
 * Public regression coverage for workspace switching (baseline contract §6):
 * 1. the previously selected workspace's items are never rendered under a
 *    newly selected workspace — not while the next load is delayed, and not
 *    when it fails;
 * 2. a mutation's late completion (held response released after the switch)
 *    stays scoped to the workspace it started in: it never closes the new
 *    workspace's form, drops its unsaved input, or announces into its live
 *    region — while the write itself still lands in the originating
 *    workspace.
 * Bruno is the seeded dual-workspace user.
 */

const BOREALIS_ITEMS = "**/api/workspaces/ws_borealis/items";
const APOLLO_ITEMS_POST = "**/api/workspaces/ws_apollo/items";
const APOLLO_ITEM_MUTATIONS = "**/api/items/*";
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

test.describe("delayed action completion stays scoped to its own workspace", () => {
  test("a held old-workspace create does not close or clear the new workspace's form", async ({
    page,
  }) => {
    let release: () => void = () => {};
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    await page.route(APOLLO_ITEMS_POST, async (route) => {
      const response = await route.fetch();
      await gate;
      await route.fulfill({ response });
    });

    // Start a create in Apollo; its POST response is held on the gate.
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Late Apollo create");
    await page.getByRole("button", { name: "Create work item" }).click();
    await expect(page.getByRole("button", { name: "Creating…" })).toBeVisible();

    // Switch to Borealis (the open form's silent discard on switch is
    // intentional baseline behavior) and start a different unsaved create.
    const selector = page.getByLabel("Workspace", { exact: true });
    const list = page.getByRole("list", { name: "Work items" });
    await selector.selectOption({ label: "Borealis Ops" });
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toBeVisible();
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Borealis unsaved draft");

    // Release the late Apollo response while Borealis is selected: it must
    // not close the Borealis form, drop its input, or announce into the
    // Borealis live region.
    release();

    await expect(page.getByLabel("Title", { exact: true })).toHaveValue("Borealis unsaved draft");
    await expect(page.getByRole("status")).toHaveText("");
    await expect(page.getByRole("alert")).toHaveCount(0);
    // The created row belongs to Apollo, not Borealis.
    await expect(list.getByRole("heading", { name: "Late Apollo create" })).toHaveCount(0);

    // Switching back proves the write landed in its own workspace.
    await selector.selectOption({ label: "Apollo Launch" });
    await expect(list.getByRole("heading", { name: "Late Apollo create" })).toBeVisible();
  });

  test("a held old-workspace delete does not change the new workspace's UI", async ({ page }) => {
    let release: () => void = () => {};
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    await page.route(APOLLO_ITEM_MUTATIONS, async (route) => {
      const response = await route.fetch();
      await gate;
      await route.fulfill({ response });
    });

    const list = page.getByRole("list", { name: "Work items" });
    await page.getByRole("button", { name: `Delete ${APOLLO_HEADING}` }).click();
    await page.getByRole("button", { name: `Confirm delete ${APOLLO_HEADING}` }).click();

    // While the DELETE response is held, switch to Borealis.
    const selector = page.getByLabel("Workspace", { exact: true });
    await selector.selectOption({ label: "Borealis Ops" });
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toBeVisible();

    // Releasing the late response must not announce, error, or disturb the
    // Borealis UI.
    release();

    await expect(page.getByRole("status")).toHaveText("");
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expect(list.getByRole("heading", { name: BOREALIS_HEADING })).toBeVisible();

    // The deletion itself did land in its own workspace.
    await selector.selectOption({ label: "Apollo Launch" });
    await expect(list.getByRole("heading", { name: APOLLO_HEADING })).toHaveCount(0);
  });
});
