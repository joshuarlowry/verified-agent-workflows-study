import { expect, test, type Page } from "@playwright/test";
import { BRUNO_EMAIL, BRUNO_PASSWORD, installMutationBarrier, signIn, waitForMutationProcessing } from "./helpers.js";

const apollo = "ws_apollo";
const borealis = "ws_borealis";

async function hold(page: Page, method: string, path: string, fail: boolean) {
  let release!: () => void;
  let arrived!: (status: number) => void;
  const gate = new Promise<void>((resolve) => { release = resolve; });
  const ready = new Promise<number>((resolve) => { arrived = resolve; });
  await page.route(`**${path}`, async (route) => {
    if (route.request().method() !== method) return route.continue();
    if (fail) {
      arrived(400);
      await gate;
      await route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({ error: { code: "validation_failed", message: "Old mutation failed.", fields: { title: "Old field error." } } }) });
    } else {
      const response = await route.fetch();
      arrived(response.status());
      await gate;
      await route.fulfill({ response });
    }
  });
  return { release, ready };
}

async function setup(page: Page) {
  await installMutationBarrier(page);
  await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
  await expect(page.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
}

async function makeTarget(page: Page, title: string): Promise<string> {
  const response = await page.request.post(`/api/workspaces/${apollo}/items`, { data: { title } });
  expect(response.status()).toBe(201);
  const item = await response.json() as { id: string };
  await page.reload();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  return item.id;
}

test.afterEach(async ({ page }) => {
  // Leave seeded rows and other public tests' data untouched.
  const response = await page.request.get(`/api/workspaces/${apollo}/items`);
  if (!response.ok()) return;
  const body = await response.json() as { items: { id: string; title: string }[] };
  for (const item of body.items) {
    if (item.title.startsWith("Isolation ") || ["ABA original", "New pending form", "Old form", "Later form"].includes(item.title)) {
      expect((await page.request.delete(`/api/items/${item.id}`)).status()).toBe(204);
    }
  }
});

for (const kind of ["create", "edit", "delete"] as const) {
  for (const fail of [false, true]) {
    test(`held ${kind} ${fail ? "failure" : "success"} cannot affect a later selection and form`, async ({ page }) => {
      await setup(page);
      const title = `Isolation ${kind} ${fail}`;
      const id = kind === "create" ? "" : await makeTarget(page, title);
      const path = kind === "create" ? `/api/workspaces/${apollo}/items` : `/api/items/${id}`;
      const method = kind === "create" ? "POST" : kind === "edit" ? "PATCH" : "DELETE";
      const held = await hold(page, method, path, fail);
      if (kind === "create") {
        await page.getByRole("button", { name: "New work item" }).click();
        await page.getByLabel("Title", { exact: true }).fill(title);
        await page.getByRole("button", { name: "Create work item" }).click();
      } else if (kind === "edit") {
        await page.getByRole("button", { name: `Edit ${title}` }).click();
        await page.getByLabel("Notes", { exact: true }).fill("saved in Apollo");
        await page.getByRole("button", { name: "Save changes" }).click();
      } else {
        await page.getByRole("button", { name: `Delete ${title}` }).click();
        await page.getByRole("button", { name: `Confirm delete ${title}` }).click();
      }
      expect(await held.ready).toBe(fail ? 400 : kind === "create" ? 201 : kind === "edit" ? 200 : 204);
      const selector = page.getByLabel("Workspace", { exact: true });
      await selector.selectOption(borealis);
      await expect(page.getByRole("heading", { name: "Rotate API keys" })).toBeVisible();
      await page.getByRole("button", { name: "Edit Rotate API keys" }).click();
      await page.getByLabel("Notes", { exact: true }).fill("Borealis unsaved draft");
      await page.getByRole("button", { name: "Delete Quarterly access review" }).click();
      held.release();
      await waitForMutationProcessing(page, method, path);
      await expect(page.getByLabel("Notes", { exact: true })).toHaveValue("Borealis unsaved draft");
      await expect(page.getByRole("button", { name: "Save changes" })).toBeEnabled();
      await expect(page.getByRole("button", { name: "Confirm delete Quarterly access review" })).toBeVisible();
      await expect(page.getByRole("status")).toHaveText("");
      await expect(page.getByRole("alert")).toHaveCount(0);
      await selector.selectOption(apollo);
      await expect(page.getByRole("heading", { name: "Fix mobile nav overflow" })).toBeVisible();
      if (kind === "create") {
        if (fail) await expect(page.getByRole("heading", { name: title, exact: true })).toHaveCount(0);
        else await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
      } else if (kind === "delete") {
        if (fail) await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
        else await expect(page.getByRole("heading", { name: title, exact: true })).toHaveCount(0);
      } else {
        await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
        const target = page.locator("li").filter({ has: page.getByRole("heading", { name: title, exact: true }) });
        if (fail) await expect(target.getByText("saved in Apollo")).toHaveCount(0);
        else await expect(target.getByText("saved in Apollo")).toBeVisible();
      }
    });
  }
}

test("ABA create completion cannot close a new Apollo form", async ({ page }) => {
  await setup(page);
  const path = `/api/workspaces/${apollo}/items`;
  const held = await hold(page, "POST", path, false);
  await page.getByRole("button", { name: "New work item" }).click();
  await page.getByLabel("Title", { exact: true }).fill("ABA original");
  await page.getByRole("button", { name: "Create work item" }).click();
  expect(await held.ready).toBe(201);
  const selector = page.getByLabel("Workspace", { exact: true });
  await selector.selectOption(borealis);
  await expect(page.getByRole("heading", { name: "Rotate API keys" })).toBeVisible();
  await selector.selectOption(apollo);
  await expect(page.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
  await page.getByRole("button", { name: "New work item" }).click();
  await page.getByLabel("Title", { exact: true }).fill("New Apollo draft");
  held.release();
  await waitForMutationProcessing(page, "POST", path);
  await expect(page.getByLabel("Title", { exact: true })).toHaveValue("New Apollo draft");
  await expect(page.getByRole("status")).toHaveText("");
  await expect(page.getByRole("alert")).toHaveCount(0);
});


for (const fail of [false, true]) {
  test(`same-selection old create ${fail ? "failure" : "success"} leaves a newer pending form alone`, async ({ page }) => {
    await setup(page);
    const path = `/api/workspaces/${apollo}/items`;
    const old = await hold(page, "POST", path, fail);
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Old form");
    await page.getByRole("button", { name: "Create work item" }).click();
    expect(await old.ready).toBe(fail ? 400 : 201);
    await page.getByRole("button", { name: "Close new item form" }).click();
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Later form");
    const current = await hold(page, "POST", path, false);
    await page.getByRole("button", { name: "Create work item" }).click();
    expect(await current.ready).toBe(201);
    old.release();
    await waitForMutationProcessing(page, "POST", path);
    await expect(page.getByRole("button", { name: "Creating…" })).toBeDisabled();
    await expect(page.getByLabel("Title", { exact: true })).toHaveValue("Later form");
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expect(page.getByRole("status")).toHaveText("");
    current.release();
    await waitForMutationProcessing(page, "POST", path, 2);
    await expect(page.getByRole("heading", { name: "Later form", exact: true })).toBeVisible();
    await expect(page.getByRole("status")).toHaveText("Work item created.");
  });
}

for (const fail of [false, true]) {
  test(`old delete ${fail ? "failure" : "success"} cannot reset a replacement confirmation`, async ({ page }) => {
    await setup(page);
    const id = await makeTarget(page, `Isolation old delete ${fail}`);
    const path = `/api/items/${id}`;
    const old = await hold(page, "DELETE", path, fail);
    await page.getByRole("button", { name: `Delete Isolation old delete ${fail}` }).click();
    await page.getByRole("button", { name: `Confirm delete Isolation old delete ${fail}` }).click();
    expect(await old.ready).toBe(fail ? 400 : 204);
    await page.getByRole("button", { name: "Delete Fix mobile nav overflow" }).click();
    old.release();
    await waitForMutationProcessing(page, "DELETE", path);
    await expect(page.getByRole("button", { name: "Confirm delete Fix mobile nav overflow" })).toBeVisible();
    await expect(page.getByRole("status")).toHaveText("");
    await expect(page.getByRole("alert")).toHaveCount(0);
  });
}

for (const kind of ["create", "edit", "delete"] as const) {
  for (const fail of [false, true]) {
    test(`ABA ${kind} ${fail ? "failure" : "success"} cannot affect a newer pending form`, async ({ page }) => {
      await setup(page);
      const title = `Isolation ABA ${kind} ${fail}`;
      const id = kind === "create" ? "" : await makeTarget(page, title);
      const path = kind === "create" ? `/api/workspaces/${apollo}/items` : `/api/items/${id}`;
      const method = kind === "create" ? "POST" : kind === "edit" ? "PATCH" : "DELETE";
      const old = await hold(page, method, path, fail);
      if (kind === "create") {
        await page.getByRole("button", { name: "New work item" }).click();
        await page.getByLabel("Title", { exact: true }).fill(title);
        await page.getByRole("button", { name: "Create work item" }).click();
      } else if (kind === "edit") {
        await page.getByRole("button", { name: `Edit ${title}` }).click();
        await page.getByLabel("Notes", { exact: true }).fill("ABA edit payload");
        await page.getByRole("button", { name: "Save changes" }).click();
      } else {
        await page.getByRole("button", { name: `Delete ${title}` }).click();
        await page.getByRole("button", { name: `Confirm delete ${title}` }).click();
      }
      expect(await old.ready).toBe(fail ? 400 : kind === "create" ? 201 : kind === "edit" ? 200 : 204);
      const selector = page.getByLabel("Workspace", { exact: true });
      await selector.selectOption(borealis);
      await expect(page.getByRole("heading", { name: "Rotate API keys" })).toBeVisible();
      await selector.selectOption(apollo);
      await expect(page.getByRole("heading", { name: "Prepare demo script" })).toBeVisible();
      let reloads = 0;
      page.on("request", (request) => {
        if (request.method() === "GET" && new URL(request.url()).pathname === `/api/workspaces/${apollo}/items`) reloads += 1;
      });
      await page.getByRole("button", { name: "New work item" }).click();
      await page.getByLabel("Title", { exact: true }).fill("Later form");
      const current = await hold(page, "POST", `/api/workspaces/${apollo}/items`, false);
      await page.getByRole("button", { name: "Create work item" }).click();
      expect(await current.ready).toBe(201);
      old.release();
      await waitForMutationProcessing(page, method, path);
      await expect(page.getByRole("button", { name: "Creating…" })).toBeDisabled();
      await expect(page.getByLabel("Title", { exact: true })).toHaveValue("Later form");
      await expect(page.getByRole("alert")).toHaveCount(0);
      await expect(page.getByRole("status")).toHaveText("");
      expect(reloads).toBe(0);
      current.release();
      await waitForMutationProcessing(page, "POST", `/api/workspaces/${apollo}/items`, kind === "create" ? 2 : 1);
      await expect(page.getByRole("heading", { name: "Later form", exact: true })).toBeVisible();
      await expect(page.getByRole("status")).toHaveText("Work item created.");
    });
  }
}

for (const fail of [false, true]) {
  test(`old edit ${fail ? "failure" : "success"} cannot close a replacement pending form`, async ({ page }) => {
    await setup(page);
    const title = `Isolation replaced edit ${fail}`;
    const id = await makeTarget(page, title);
    const path = `/api/items/${id}`;
    const old = await hold(page, "PATCH", path, fail);
    await page.getByRole("button", { name: `Edit ${title}` }).click();
    await page.getByLabel("Notes", { exact: true }).fill("old edit payload");
    await page.getByRole("button", { name: "Save changes" }).click();
    expect(await old.ready).toBe(fail ? 400 : 200);
    await page.getByRole("button", { name: "New work item" }).click();
    await page.getByLabel("Title", { exact: true }).fill("Later form");
    const current = await hold(page, "POST", `/api/workspaces/${apollo}/items`, false);
    await page.getByRole("button", { name: "Create work item" }).click();
    expect(await current.ready).toBe(201);
    old.release();
    await waitForMutationProcessing(page, "PATCH", path);
    await expect(page.getByRole("button", { name: "Creating…" })).toBeDisabled();
    await expect(page.getByLabel("Title", { exact: true })).toHaveValue("Later form");
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expect(page.getByRole("status")).toHaveText("");
    current.release();
    await waitForMutationProcessing(page, "POST", `/api/workspaces/${apollo}/items`);
    await expect(page.getByRole("heading", { name: "Later form", exact: true })).toBeVisible();
    await expect(page.getByRole("status")).toHaveText("Work item created.");
  });
}

for (const fail of [false, true]) {
  test(`old delete ${fail ? "failure" : "success"} cannot disturb a later same-selection form`, async ({ page }) => {
    await setup(page);
    const title = `Isolation delete form ${fail}`;
    const id = await makeTarget(page, title);
    const path = `/api/items/${id}`;
    const old = await hold(page, "DELETE", path, fail);
    await page.getByRole("button", { name: `Delete ${title}` }).click();
    await page.getByRole("button", { name: `Confirm delete ${title}` }).click();
    expect(await old.ready).toBe(fail ? 400 : 204);
    await page.getByRole("button", { name: "Edit Fix mobile nav overflow" }).click();
    await page.getByLabel("Notes", { exact: true }).fill("later edit draft");
    let reloads = 0;
    page.on("request", (request) => {
      if (request.method() === "GET" && new URL(request.url()).pathname === `/api/workspaces/${apollo}/items`) reloads += 1;
    });
    old.release();
    await waitForMutationProcessing(page, "DELETE", path);
    await expect(page.getByLabel("Notes", { exact: true })).toHaveValue("later edit draft");
    await expect(page.getByRole("status")).toHaveText("");
    await expect(page.getByRole("alert")).toHaveCount(0);
    expect(reloads).toBe(0);
    const response = await page.request.get(`/api/workspaces/${apollo}/items`);
    const body = await response.json() as { items: { id: string }[] };
    expect(body.items.some((item) => item.id === id)).toBe(fail);
  });
}
