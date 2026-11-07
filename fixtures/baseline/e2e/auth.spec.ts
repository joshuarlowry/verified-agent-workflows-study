import { expect, test } from "@playwright/test";
import {
  ADA_EMAIL,
  ADA_PASSWORD,
  BRUNO_EMAIL,
  BRUNO_PASSWORD,
  CLEO_EMAIL,
  CLEO_PASSWORD,
  signIn,
  signOut,
} from "./helpers.js";

test.describe("authentication", () => {
  test("shows a labeled sign-in form with semantic controls", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Sign in to Workboard Lab" })).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  });

  test("a wrong password surfaces an alert, not a navigation", async ({ page }) => {
    await page.goto("/");
    await page.getByLabel("Email").fill(ADA_EMAIL);
    await page.getByLabel("Password").fill("totally-wrong-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.getByRole("alert").first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Sign in to Workboard Lab" })).toBeVisible();
  });

  test("seeded ada signs in and sees exactly her workspace with the owner role", async ({ page }) => {
    await signIn(page, ADA_EMAIL, ADA_PASSWORD);
    await expect(page.getByText(ADA_EMAIL)).toBeVisible();
    const options = page.getByLabel("Workspace", { exact: true }).locator("option");
    await expect(options).toHaveText(["Apollo Launch"]);
    await expect(page.getByText("Your role: Owner")).toBeVisible();
  });

  test("seeded cleo only sees the workspace she belongs to", async ({ page }) => {
    await signIn(page, CLEO_EMAIL, CLEO_PASSWORD);
    const options = page.getByLabel("Workspace", { exact: true }).locator("option");
    await expect(options).toHaveText(["Borealis Ops"]);
    await expect(page.getByText("Your role: Member")).toBeVisible();
  });

  test("seeded bruno sees both workspaces (member of Apollo, owner of Borealis)", async ({ page }) => {
    await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
    const options = page.getByLabel("Workspace", { exact: true }).locator("option");
    await expect(options).toHaveText(["Apollo Launch", "Borealis Ops"]);
    // Workspaces are listed in name order; Apollo is selected first.
    await expect(page.getByText("Your role: Member")).toBeVisible();
  });

  test("sign out returns to the sign-in screen and the session is really gone", async ({ page }) => {
    await signIn(page, ADA_EMAIL, ADA_PASSWORD);
    await signOut(page);
    // Reload: no session cookie means the sign-in panel again, not the app.
    await page.reload();
    await expect(page.getByRole("heading", { name: "Sign in to Workboard Lab" })).toBeVisible();
  });

  test("sign-up creates a fresh account whose first workspace flow works", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Need an account? Create one" }).click();
    await page.getByLabel("Name").fill("Dora Example");
    await page.getByLabel("Email").fill("dora@workboard.test");
    await page.getByLabel("Password").fill("dora-passphrase-04");
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByRole("heading", { name: "Create your first workspace" })).toBeVisible();
    await page.getByLabel("Workspace name").fill("Dora Lab");
    await page.getByRole("button", { name: "Create workspace" }).click();

    await expect(page.getByLabel("Workspace", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Workspace", { exact: true }).locator("option")).toHaveText(["Dora Lab"]);
    await expect(
      page.getByText(/No work items in this workspace yet/)
    ).toBeVisible();
    await signOut(page);
  });
});
