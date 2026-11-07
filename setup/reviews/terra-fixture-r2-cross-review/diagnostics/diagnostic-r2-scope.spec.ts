// REVIEW-AUTHORED DIAGNOSTIC ONLY — demonstrates unwanted baseline behavior, not acceptance coverage.
import { expect, test } from '@playwright/test';
import { BRUNO_EMAIL, BRUNO_PASSWORD, signIn } from './helpers.js';

test('held Apollo edit response closes Borealis edit', async ({page}) => {
  await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
  let release!: () => void;
  let ready!: () => void;
  const gate = new Promise<void>(r => {release = r;});
  const arrived = new Promise<void>(r => {ready = r;});
  await page.route('**/api/items/wi_103', async route => {
    if (route.request().method() !== 'PATCH') return route.continue();
    const response = await route.fetch();
    console.log('Apollo PATCH actual status', response.status());
    ready();
    await gate;
    await route.fulfill({response});
  });
  await page.getByRole('button',{name:'Edit Prepare demo script'}).click();
  await page.getByLabel('Notes',{exact:true}).fill('old workspace change');
  await page.getByRole('button',{name:'Save changes'}).click();
  await arrived;
  await page.getByLabel('Workspace',{exact:true}).selectOption({label:'Borealis Ops'});
  await page.getByRole('button',{name:'Edit Rotate API keys'}).click();
  await page.getByLabel('Notes',{exact:true}).fill('Borealis unsaved diagnostic draft');
  const response = page.waitForResponse(r => r.url().endsWith('/api/items/wi_103') && r.request().method()==='PATCH');
  release();
  await response;
  await expect(page.getByLabel('Notes',{exact:true})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Edit Rotate API keys'})).toBeVisible();
  console.log('OBSERVED: Borealis edit form vanished, unsaved notes lost after Apollo response.');
});

test('held create after switch away and back closes later form', async ({page}) => {
  await signIn(page, BRUNO_EMAIL, BRUNO_PASSWORD);
  let release!: () => void; let ready!: () => void;
  const gate = new Promise<void>(r => {release = r;});
  const arrived = new Promise<void>(r => {ready = r;});
  await page.route('**/api/workspaces/ws_apollo/items', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    const response = await route.fetch(); ready(); await gate; await route.fulfill({response});
  });
  await page.getByRole('button',{name:'New work item'}).click();
  await page.getByLabel('Title',{exact:true}).fill('diagnostic ABA create');
  await page.getByRole('button',{name:'Create work item'}).click();
  await arrived;
  const select = page.getByLabel('Workspace',{exact:true});
  await select.selectOption({label:'Borealis Ops'});
  await expect(page.getByRole('heading',{name:'Rotate API keys'})).toBeVisible();
  await select.selectOption({label:'Apollo Launch'});
  await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  await page.getByRole('button',{name:'New work item'}).click();
  await page.getByLabel('Title',{exact:true}).fill('new Apollo draft after return');
  const response = page.waitForResponse(r => r.url().endsWith('/api/workspaces/ws_apollo/items') && r.request().method()==='POST');
  release(); await response;
  await expect(page.getByLabel('Title',{exact:true})).toHaveCount(0);
  await expect(page.getByRole('status')).toHaveText('Work item created.');
  console.log('OBSERVED: returned-to-Apollo new draft vanished and stale response announced.');
});
