// REVIEW DIAGNOSTIC ONLY. Not a fixture test or task implementation.
import { test, expect } from '@playwright/test';
import { signIn, BRUNO_EMAIL, BRUNO_PASSWORD } from './helpers.js';

test('late Apollo create completion closes a new Borealis form', async ({ page }) => {
  await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
  await expect(page.getByRole('heading', { name: 'Prepare demo script' })).toBeVisible();
  let release!: () => void;
  let fetched!: () => void;
  const gate = new Promise<void>((r) => { release = r; });
  const reached = new Promise<void>((r) => { fetched = r; });
  await page.route('**/api/workspaces/ws_apollo/items', async (route) => {
    if (route.request().method() !== 'POST') return route.continue();
    const response = await route.fetch();
    fetched();
    await gate;
    await route.fulfill({ response });
  });
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title', { exact: true }).fill('Apollo pending diagnostic');
  await page.getByRole('button', { name: 'Create work item' }).click();
  await reached;
  await page.getByLabel('Workspace', { exact: true }).selectOption({ label: 'Borealis Ops' });
  await expect(page.getByRole('heading', { name: 'Rotate API keys' })).toBeVisible();
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title', { exact: true }).fill('Borealis unsaved diagnostic');
  await expect(page.getByLabel('Title', { exact: true })).toHaveValue('Borealis unsaved diagnostic');
  release();
  await expect(page.getByLabel('Title', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('status')).toHaveText('Work item created.');
  await expect(page.getByLabel('Workspace', { exact: true })).toHaveValue('ws_borealis');
  const apollo = await (await page.request.get('/api/workspaces/ws_apollo/items')).json();
  const borealis = await (await page.request.get('/api/workspaces/ws_borealis/items')).json();
  expect(apollo.items.some((x: {title:string}) => x.title === 'Apollo pending diagnostic')).toBe(true);
  expect(borealis.items.some((x: {title:string}) => x.title === 'Apollo pending diagnostic')).toBe(false);
});
