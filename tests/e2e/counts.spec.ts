import { test, expect } from '@playwright/test';

test('workspace item counts', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Need an account? Create one' }).click();
  await page.getByLabel('Name', { exact: true }).fill('Test User');
  await page.getByLabel('Email').fill(`test-${Date.now()}@workboard.test`);
  await page.getByLabel('Password').fill('password-123');
  await page.getByRole('button', { name: 'Create account' }).click();

  // Create a workspace
  await page.getByLabel('Workspace name').fill('Count Workspace');
  await page.getByRole('button', { name: 'Create workspace' }).click();

  // Assert count is 0
  const select = page.getByRole('combobox', { name: 'Workspace' });
  
  const optionText = await select.evaluate((el: HTMLSelectElement) => {
    return el.options[el.selectedIndex].text;
  });
  expect(optionText).toBe('Count Workspace (0)');

  // Create an open work item
  await page.getByRole('button', { name: 'New work item' }).click();
  await page.getByLabel('Title').fill('Test Item');
  await page.getByRole('button', { name: 'Create work item' }).click();

  // Reload the page to refresh counts
  await page.reload();

  // Assert count is 1
  const optionTextAfter = await select.evaluate((el: HTMLSelectElement) => {
    return el.options[el.selectedIndex].text;
  });
  expect(optionTextAfter).toBe('Count Workspace (1)');
});
