import { expect, test } from "@playwright/test";
import { BRUNO_EMAIL, BRUNO_PASSWORD, CLEO_EMAIL, CLEO_PASSWORD, signIn } from "./helpers.js";

test.describe("workspace ownership and visibility in the UI", () => {
  test("a non-member never sees another workspace's items", async ({ page }) => {
    await signIn(page, CLEO_EMAIL, CLEO_PASSWORD);
    const list = page.getByRole("list", { name: "Work items" });
    await expect(list.getByRole("heading", { name: "Rotate API keys" })).toBeVisible();
    // Apollo-only seeded items must never appear for Cleo.
    await expect(list.getByRole("heading", { name: "Draft launch checklist" })).toHaveCount(0);
    await expect(list.getByRole("heading", { name: "Prepare demo script" })).toHaveCount(0);
  });

  test("a member of two workspaces can switch and sees the right items", async ({ page }) => {
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    const selector = page.getByLabel("Workspace", { exact: true });
    const list = page.getByRole("list", { name: "Work items" });

    await expect(list.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
    await expect(list.getByRole("heading", { name: "Rotate API keys" })).toHaveCount(0);

    await selector.selectOption({ label: "Borealis Ops" });
    await expect(list.getByRole("heading", { name: "Rotate API keys" })).toBeVisible();
    await expect(list.getByRole("heading", { name: "Prepare demo script" })).toHaveCount(0);

    await selector.selectOption({ label: "Apollo Launch" });
    await expect(list.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
  });

  test("role labels follow the selected workspace's membership", async ({ page }) => {
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    await expect(page.getByText("Your role: Member")).toBeVisible(); // Apollo
    await page
      .getByLabel("Workspace", { exact: true })
      .selectOption({ label: "Borealis Ops" });
    await expect(page.getByText("Your role: Owner")).toBeVisible();
  });
});
