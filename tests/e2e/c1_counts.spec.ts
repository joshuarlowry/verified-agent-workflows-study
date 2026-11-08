import { test, expect } from '@playwright/test';

test('workspace open item counts are current and reflect changes', async ({ page }) => {
  // Use a fresh account to be order-independent and self-contained
  const email = `user-${Date.now()}@workboard.test`;
  const password = 'password-123';
  await page.goto('/');
  await page.getByRole('button',{name:'Need an account? Create one'}).click();
  await page.getByLabel('Name').fill('Test User');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button',{name:'Create account'}).click();
  await expect(page.getByRole('heading',{name:'Create your first workspace'})).toBeVisible();

  const wsName = 'C1 Workspace';
  await page.getByLabel('Workspace name').fill(wsName);
  await page.getByRole('button',{name:'Create workspace'}).click();
  await expect(page.getByText('Workspace created.')).toBeVisible();

  // Newly created workspace should display (0)
  // We use a locator that finds the option based on the name.
  await expect(page.locator('select')).toContainText(`${wsName} (0)`);

  // Create open item
  await page.getByRole('button',{name:'New work item'}).click();
  await page.getByLabel('Title').fill('Open Item');
  await page.getByRole('button',{name:'Create work item'}).click();
  await expect(page.getByText('Work item created.')).toBeVisible();

  // Refresh to see updated count
  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (1)`);

  // Transition to in_progress
  await page.getByRole('button',{name:'Edit Open Item'}).click();
  await page.getByLabel('Status').selectOption('in_progress');
  await page.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByText('Work item updated.')).toBeVisible();

  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (0)`);

  // Transition back to open
  await page.getByRole('button',{name:'Edit Open Item'}).click();
  await page.getByLabel('Status').selectOption('open');
  await page.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByText('Work item updated.')).toBeVisible();

  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (1)`);

  // Transition to done
  await page.getByRole('button',{name:'Edit Open Item'}).click();
  await page.getByLabel('Status').selectOption('done');
  await page.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByText('Work item updated.')).toBeVisible();

  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (0)`);

  // Create another open item and delete it
  await page.getByRole('button',{name:'New work item'}).click();
  await page.getByLabel('Title').fill('Delete Item');
  await page.getByRole('button',{name:'Create work item'}).click();
  await expect(page.getByText('Work item created.')).toBeVisible();

  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (1)`);

  await page.getByRole('button',{name:'Delete Delete Item'}).click();
  await page.getByRole('button',{name:'Confirm delete Delete Item'}).click();
  await expect(page.getByText('Work item deleted.')).toBeVisible();

  await page.reload();
  await expect(page.locator('select')).toContainText(`${wsName} (0)`);
});
