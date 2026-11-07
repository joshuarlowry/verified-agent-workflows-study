import { expect, test } from "@playwright/test";
import { ADA_EMAIL, ADA_PASSWORD, createItem, signIn } from "./helpers.js";

test.describe.serial("work item CRUD through the real UI + API + database", () => {
  test.beforeEach(async ({ page }) => {
    await signIn(page, ADA_EMAIL, ADA_PASSWORD);
  });

  test("lists seeded items with semantic status labels and due dates", async ({ page }) => {
    const list = page.getByRole("list", { name: "Work items" });
    await expect(list).toBeVisible();

    // Newest-first: wi_103 was updated last in the seed.
    await expect(
      list.getByRole("heading", { name: "Prepare demo script" })
    ).toBeVisible();
    await expect(
      list.getByRole("heading", { name: "Draft launch checklist" })
    ).toBeVisible();

    const checklistCard = list.locator("li", { has: page.getByRole("heading", { name: "Draft launch checklist" }) });
    await expect(checklistCard.getByText("Open", { exact: true })).toBeVisible();
    await expect(checklistCard.getByText("Due 2026-11-12")).toBeVisible();

    const pricingCard = list.locator("li", { has: page.getByRole("heading", { name: "Review pricing copy" }) });
    await expect(pricingCard.getByText("In progress", { exact: true })).toBeVisible();

    const emailCard = list.locator("li", { has: page.getByRole("heading", { name: "Ship onboarding email" }) });
    await expect(emailCard.getByText("Done", { exact: true })).toBeVisible();

    const demoCard = list.locator("li", { has: page.getByRole("heading", { name: "Prepare demo script" }) });
    await expect(demoCard.getByText("No due date")).toBeVisible();
  });

  test("creating an item persists it across a full page reload", async ({ page }) => {
    const title = "E2E persistence probe item";
    await createItem(page, {
      title,
      notes: "Must survive a reload.",
      dueDate: "2026-11-25",
      status: "In progress",
    });
    const card = page.getByRole("list", { name: "Work items" }).locator("li", {
      has: page.getByRole("heading", { name: title }),
    });
    await expect(card.getByText("In progress", { exact: true })).toBeVisible();
    await expect(card.getByText("Due 2026-11-25")).toBeVisible();
    await expect(card.getByText("Must survive a reload.")).toBeVisible();

    // A reload forces a round-trip through the API and SQLite.
    await page.reload();
    await expect(
      page.getByRole("list", { name: "Work items" }).getByRole("heading", { name: title })
    ).toBeVisible();
  });

  test("editing an item updates the stored data", async ({ page }) => {
    const title = "E2E edit probe item";
    await createItem(page, { title });

    await page.getByRole("button", { name: `Edit ${title}` }).click();
    const titleField = page.getByLabel("Title", { exact: true });
    await expect(titleField).toHaveValue(title);
    await titleField.fill("E2E edit probe item v2");
    await page.getByLabel("Status", { exact: true }).selectOption({ label: "Done" });
    await page.getByRole("button", { name: "Save changes" }).click();

    const list = page.getByRole("list", { name: "Work items" });
    await expect(list.getByRole("heading", { name: "E2E edit probe item v2" })).toBeVisible();
    await expect(list.getByRole("heading", { name: title, exact: true })).toHaveCount(0);
    const card = list.locator("li", {
      has: page.getByRole("heading", { name: "E2E edit probe item v2" }),
    });
    await expect(card.getByText("Done", { exact: true })).toBeVisible();

    await page.reload();
    await expect(
      page.getByRole("list", { name: "Work items" }).getByRole("heading", { name: "E2E edit probe item v2" })
    ).toBeVisible();
  });

  test("deleting requires an explicit confirm step and then removes the item", async ({ page }) => {
    const title = "E2E delete probe item";
    await createItem(page, { title });

    await page.getByRole("button", { name: `Delete ${title}` }).click();
    // Nothing is deleted before confirmation.
    await expect(page.getByRole("button", { name: `Confirm delete ${title}` })).toBeVisible();
    await expect(
      page.getByRole("list", { name: "Work items" }).getByRole("heading", { name: title })
    ).toBeVisible();

    await page.getByRole("button", { name: `Cancel` }).click();
    await expect(page.getByRole("button", { name: `Confirm delete ${title}` })).toHaveCount(0);

    await page.getByRole("button", { name: `Delete ${title}` }).click();
    await page.getByRole("button", { name: `Confirm delete ${title}` }).click();
    await expect(
      page.getByRole("list", { name: "Work items" }).getByRole("heading", { name: title, exact: true })
    ).toHaveCount(0);
  });

  test("submitting an empty title surfaces the baseline validation message", async ({ page }) => {
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByRole("button", { name: "Create work item" }).click();
    await expect(page.getByRole("alert")).toContainText("Invalid work item input.");
    await expect(page.getByText("title must be a non-empty string.")).toBeVisible();
    // The form stays open so the user can correct the input.
    await expect(page.getByLabel("Title", { exact: true })).toBeVisible();
  });

  test("cancel closes the new-item form without creating anything", async ({ page }) => {
    const list = page.getByRole("list", { name: "Work items" });
    await expect(list.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
    const before = await list.locator("li").count();
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Never created");
    await page.getByRole("button", { name: "Cancel" }).click();
    await expect(page.getByLabel("Title", { exact: true })).toHaveCount(0);
    await expect(list.getByRole("heading", { name: "Never created" })).toHaveCount(0);
    const after = await list.locator("li").count();
    expect(after).toBe(before);
  });
});
