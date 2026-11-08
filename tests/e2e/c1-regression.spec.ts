import { test, expect, type Page } from '@playwright/test';
import Database from 'better-sqlite3';

async function login(page:Page,email='bruno@workboard.test',password='bruno-passphrase-02') {
  await page.goto('/'); await page.getByLabel('Email').fill(email); await page.getByLabel('Password').fill(password); await page.getByRole('button',{name:'Sign in',exact:true}).click();
  await expect(page.getByRole('combobox',{name:'Workspace',exact:true})).toBeVisible();
}

test('C1 - Workspace labels and zero counts', async ({ page }) => {
  await login(page);
  
  // Seeded labels
  await expect(page.locator('option[value="ws_apollo"]')).toHaveText('Apollo Launch (4)');
  await expect(page.locator('option[value="ws_borealis"]')).toHaveText('Borealis Ops (3)');

  // Create new workspace
  await page.getByLabel('Workspace name').fill('Zero Space');
  await page.getByRole('button', { name: 'Create workspace' }).click();
  
  // Immediate zero count for new workspace
  // Option elements are generally not 'visible' in the same way as other elements in Playwright.
  await expect(page.locator('option[value="ws_apollo"]')).toBeAttached(); // Ensure we are back
  await expect(page.getByRole('option').filter({ hasText: 'Zero Space (0)' })).toBeAttached();

  // Add an item to Zero Space
  await page.getByRole('combobox', { name: 'Workspace', exact: true }).selectOption({ label: 'Zero Space (0)' });
  
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title').fill('First Item');
  await page.getByRole('button', { name: 'Create work item' }).click();
  
  // After creation, the board refreshes, but the select options are from the 'me' state.
  await expect(page.getByRole('option').filter({ hasText: 'Zero Space (1)' })).toBeAttached();
});

test('C1 - Fresh page reload reflects item changes', async ({ page }) => {
  await login(page);
  
  // Apollo has 4 open. Create one more.
  await page.getByRole('combobox', { name: 'Workspace', exact: true }).selectOption('ws_apollo');
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title').fill('Reload Test Item');
  await page.getByRole('button', { name: 'Create work item' }).click();
  
  // Reload page
  await page.reload();
  await expect(page.locator('option[value="ws_apollo"]')).toHaveText('Apollo Launch (5)');
});

test('C1 - Switching workspaces reflects current counts', async ({ page }) => {
  await login(page);
  
  // Create an item in Apollo
  await page.getByRole('combobox', { name: 'Workspace', exact: true }).selectOption('ws_apollo');
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title').fill('Switch Test Item');
  await page.getByRole('button', { name: 'Create work item' }).click();
  
  // Switch to Borealis
  await page.getByRole('combobox', { name: 'Workspace', exact: true }).selectOption('ws_borealis');
  await expect(page.locator('option[value="ws_borealis"]')).toHaveText('Borealis Ops (3)');
  
  // Switch back to Apollo
  await page.getByRole('combobox', { name: 'Workspace', exact: true }).selectOption('ws_apollo');
  await expect(page.locator('option[value="ws_apollo"]')).toHaveText('Apollo Launch (5)');
});
