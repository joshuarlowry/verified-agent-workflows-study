import { test, expect } from '@playwright/test';

test('workspace labels show fresh open counts and preserve switching',async({page})=>{
  await page.goto('/'); await page.getByRole('button',{name:'Need an account? Create one'}).click();
  await page.getByLabel('Name',{exact:true}).fill('Count Test'); await page.getByLabel('Email').fill('ui-counts@workboard.test'); await page.getByLabel('Password').fill('password-123'); await page.getByRole('button',{name:'Create account'}).click();
  await expect(page.getByRole('heading',{name:'Create your first workspace'})).toBeVisible();
  await page.getByLabel('Workspace name').fill('Count Alpha'); await page.getByRole('button',{name:'Create workspace'}).click();
  const selector=page.getByRole('combobox',{name:'Workspace',exact:true});
  await expect(selector.locator('option')).toHaveText(['Count Alpha (0)']);
  await page.getByLabel('Workspace name').fill('Count Beta'); await page.getByRole('button',{name:'Create workspace'}).click();
  await expect(selector.locator('option')).toHaveText(['Count Alpha (0)','Count Beta (0)']);
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('Counted item'); await page.getByRole('button',{name:'Create work item'}).click();
  await expect(page.getByRole('heading',{name:'Counted item'})).toBeVisible();
  await page.reload(); await expect(selector.locator('option')).toHaveText(['Count Alpha (0)','Count Beta (1)']);
  await selector.selectOption({label:'Count Beta (1)'}); await expect(page.getByRole('heading',{name:'Counted item'})).toBeVisible();
  await page.getByRole('button',{name:'Edit Counted item'}).click(); await page.getByLabel('Status').selectOption('done'); await page.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByText('Work item updated.')).toBeVisible();
  await page.reload(); await expect(selector.locator('option')).toHaveText(['Count Alpha (0)','Count Beta (0)']);
  await selector.selectOption({label:'Count Beta (0)'}); await expect(page.getByRole('heading',{name:'Counted item'})).toBeVisible();
});
