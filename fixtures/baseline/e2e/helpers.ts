/// <reference lib="dom" />
import { expect, type Page } from "@playwright/test";

/** Observe consumption of a mutation response, then allow its promise continuations
 * and React's next render frames to run. A network response alone is not a UI
 * processing barrier. Install before navigation. */
export async function installMutationBarrier(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const state: Record<string, number> = {};
    (window as unknown as { mutationBarrier: Record<string, number> }).mutationBarrier = state;
    const original = window.fetch.bind(window);
    window.fetch = async (input, init) => {
      const response = await original(input, init);
      const method = (init?.method ?? "GET").toUpperCase();
      if (!["POST", "PATCH", "DELETE"].includes(method)) return response;
      const url = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url, location.href);
      const key = `${method} ${url.pathname}`;
      const processed = () => {
        // The timer follows response consumption and its microtasks; two
        // animation frames allow React's scheduled commit to finish.
        setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(() => {
          state[key] = (state[key] ?? 0) + 1;
        })), 0);
      };
      if (response.status === 204) processed();
      else {
        const json = response.json.bind(response);
        response.json = async () => {
          try { return await json(); } finally { processed(); }
        };
      }
      return response;
    };
  });
}

export async function waitForMutationProcessing(page: Page, method: string, path: string, count = 1): Promise<void> {
  await page.waitForFunction(({ key, count }) =>
    ((window as unknown as { mutationBarrier: Record<string, number> }).mutationBarrier?.[key] ?? 0) >= count,
  { key: `${method} ${path}`, count });
}

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
