import { test, expect, type Page } from '@playwright/test';
import Database from 'better-sqlite3';

async function login(page:Page,email='bruno@workboard.test',password='bruno-passphrase-02') {
  await page.goto('/'); await page.getByLabel('Email').fill(email); await page.getByLabel('Password').fill(password); await page.getByRole('button',{name:'Sign in',exact:true}).click();
  await expect(page.getByRole('combobox',{name:'Workspace',exact:true})).toBeVisible();
}
function barrier() { let release!:()=>void; const promise=new Promise<void>(r=>{release=r;}); return {promise,release}; }

test('real signup, first workspace, CRUD and sign out',async({page})=>{
  await page.goto('/'); await page.getByRole('button',{name:'Need an account? Create one'}).click();
  await page.getByLabel('Name',{exact:true}).fill('New Test'); await page.getByLabel('Email').fill('ui-new@workboard.test'); await page.getByLabel('Password').fill('password-123'); await page.getByRole('button',{name:'Create account'}).click();
  await expect(page.getByRole('heading',{name:'Create your first workspace'})).toBeVisible();
  await page.getByLabel('Workspace name').fill('UI workspace'); await page.getByRole('button',{name:'Create workspace'}).click();
  await expect(page.getByText('Your role: Owner')).toBeVisible(); await expect(page.getByText('Workspace created.')).toBeVisible();
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('UI entry'); await page.getByLabel('Notes').fill('A note\nsecond line'); await page.getByRole('button',{name:'Create work item'}).click();
  await expect(page.getByText('Work item created.')).toBeVisible(); await expect(page.getByRole('heading',{name:'UI entry'})).toBeVisible();
  await page.getByRole('button',{name:'Edit UI entry'}).click(); await page.getByLabel('Title').fill('Updated UI entry'); await page.getByLabel('Status').selectOption('done'); await page.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByText('Work item updated.')).toBeVisible(); await expect(page.getByRole('heading',{name:'Updated UI entry'})).toBeVisible();
  await page.getByRole('button',{name:'Delete Updated UI entry'}).click(); await page.getByRole('button',{name:'Confirm delete Updated UI entry'}).click(); await expect(page.getByText('Work item deleted.')).toBeVisible();
  await page.getByRole('button',{name:'Sign out'}).click(); await expect(page.getByRole('button',{name:'Sign in',exact:true})).toBeVisible();
  await page.getByLabel('Email').fill('ui-new@workboard.test'); await page.getByLabel('Password').fill('password-123'); await page.getByRole('button',{name:'Sign in',exact:true}).click(); await expect(page.getByText('Your role: Owner')).toBeVisible();
});

test('failed validation preserves values and accessible field error',async({page})=>{
  await login(page); await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Notes').fill('preserve'); await page.getByRole('button',{name:'Create work item'}).click();
  await expect(page.getByRole('alert')).toContainText('Invalid work item input.'); await expect(page.getByLabel('Title')).toHaveAttribute('aria-invalid','true'); await expect(page.getByText('title must be a non-empty string.')).toBeVisible(); await expect(page.getByLabel('Notes')).toHaveValue('preserve');
});

test('delayed and failed selection loads clear old rows, retry',async({page})=>{
  await login(page); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  const arrived=barrier(), held=barrier();
  await page.route('**/api/workspaces/ws_borealis/items',async route=>{ arrived.release(); await held.promise; await route.fulfill({status:500,contentType:'application/json',body:JSON.stringify({error:{message:'load failed'}})}); },{times:1});
  await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_borealis'); await arrived.promise;
  await expect(page.getByText('Loading work items…')).toBeVisible(); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toHaveCount(0);
  held.release(); await expect(page.getByRole('alert')).toContainText('load failed'); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toHaveCount(0);
  await page.getByRole('button',{name:'Retry'}).click(); await expect(page.getByRole('heading',{name:'Update status page template'})).toBeVisible();
});

test('late save across selection ABA persists but cannot close new form or announce or reload',async({page})=>{
  await login(page); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  const arrived=barrier(), held=barrier(); let lists=0;
  page.on('request',r=>{if (r.method()==='GET' && r.url().endsWith('/api/workspaces/ws_apollo/items')) lists++;});
  await page.route('**/api/workspaces/ws_apollo/items',async route=>{ if (route.request().method() !== 'POST') return route.continue(); const response=await route.fetch(); arrived.release(); await held.promise; await route.fulfill({response}); },{times:1});
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('Late ABA'); await page.getByRole('button',{name:'Create work item'}).click(); await arrived.promise;
  const db=new Database('data/e2e.sqlite',{readonly:true}); expect(db.prepare('SELECT title FROM item WHERE title=?').get('Late ABA')).toEqual({title:'Late ABA'}); db.close();
  await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_borealis'); await expect(page.getByRole('heading',{name:'Update status page template'})).toBeVisible();
  await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_apollo'); await expect(page.getByRole('heading',{name:'Late ABA'})).toBeVisible();
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('New lifetime'); const count=lists;
  const completed=page.waitForResponse(r=>r.url().endsWith('/api/workspaces/ws_apollo/items') && r.request().method()==='POST'); held.release(); await completed;
  await expect(page.getByLabel('Title')).toHaveValue('New lifetime'); await expect(page.getByText('Work item created.')).toHaveCount(0); expect(lists).toBe(count);
});

test('old save error cannot affect replacement form',async({page})=>{
  await login(page); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible(); const arrived=barrier(), held=barrier();
  await page.route('**/api/workspaces/ws_apollo/items',async route=>{if(route.request().method()!=='POST') return route.continue(); arrived.release(); await held.promise; await route.fulfill({status:400,contentType:'application/json',body:JSON.stringify({error:{message:'old failure',fields:{title:'old error'}}})}); },{times:1});
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('old'); await page.getByRole('button',{name:'Create work item'}).click(); await arrived.promise;
  await page.getByRole('button',{name:'Cancel',exact:true}).click(); await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('replacement');
  const completed=page.waitForResponse(r=>r.url().endsWith('/api/workspaces/ws_apollo/items') && r.request().method()==='POST'); held.release(); await completed;
  await expect(page.getByLabel('Title')).toHaveValue('replacement'); await expect(page.getByText('old failure')).toHaveCount(0); await expect(page.getByRole('button',{name:'Create work item'})).toBeEnabled();
});

test('stale delete completion cannot dismiss replacement confirmation',async({page})=>{
  await login(page); await expect(page.getByRole('heading',{name:'Archive old assets'})).toBeVisible();
  const arrived=barrier(), held=barrier();
  await page.route('**/api/items/wi_108',async route=>{const response=await route.fetch(); arrived.release(); await held.promise; await route.fulfill({response});},{times:1});
  await page.getByRole('button',{name:'Delete Archive old assets'}).click(); await page.getByRole('button',{name:'Confirm delete Archive old assets'}).click(); await arrived.promise;
  await page.getByRole('button',{name:'Cancel',exact:true}).click(); await page.getByRole('button',{name:'Delete Prepare demo script'}).click();
  const complete=page.waitForResponse(r=>r.url().endsWith('/api/items/wi_108') && r.request().method()==='DELETE'); held.release(); await complete;
  await expect(page.getByRole('button',{name:'Confirm delete Prepare demo script'})).toBeVisible(); await expect(page.getByText('Work item deleted.')).toHaveCount(0);
  const db=new Database('data/e2e.sqlite',{readonly:true}); expect(db.prepare('SELECT id FROM item WHERE id=?').get('wi_108')).toBeUndefined(); db.close();
});
