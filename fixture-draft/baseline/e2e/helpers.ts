import { expect, type Page } from "@playwright/test";

export const ADA_EMAIL = "ada@workboard.test";
export const ADA_PASSWORD = "ada-passphrase-01";
export const BRUNO_EMAIL = "bruno@workboard.test";
export const BRUNO_PASSWORD = "bruno-passphrase-02";
export const CLEO_EMAIL = "cleo@workboard.test";
export const CLEO_PASSWORD = "cleo-passphrase-03";

/** Sign in through the real UI form and wait for the workspace selector. */
export async function signIn(page: Page, email: string, password: string): Promise<void> {
  await page.goto("/");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByLabel("Workspace", { exact: true })).toBeVisible({ timeout: 15_000 });
}

export async function signOut(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page.getByRole("heading", { name: "Sign in to Workboard Lab" })).toBeVisible();
}

/** Open the new-item form, fill it and submit. */
export async function createItem(
  page: Page,
  values: { title: string; notes?: string; dueDate?: string; status?: "Open" | "In progress" | "Done" }
): Promise<void> {
  await page.getByRole("button", { name: "New work item" }).click();
  await page.getByLabel("Title", { exact: true }).fill(values.title);
  if (values.notes !== undefined) {
    await page.getByLabel("Notes", { exact: true }).fill(values.notes);
  }
  if (values.dueDate !== undefined) {
    await page.getByLabel("Due date", { exact: true }).fill(values.dueDate);
  }
  if (values.status !== undefined) {
    await page.getByLabel("Status", { exact: true }).selectOption({ label: values.status });
  }
  await page.getByRole("button", { name: "Create work item" }).click();
  await expect(
    page.getByRole("heading", { name: values.title, exact: true })
  ).toBeVisible({ timeout: 15_000 });
}
