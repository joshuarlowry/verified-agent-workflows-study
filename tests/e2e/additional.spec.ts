import { test, expect, type Page } from '@playwright/test';
import Database from 'better-sqlite3';
const signal = () => { let release!:()=>void; const promise = new Promise<void>(r=>{release=r;}); return {promise,release}; };
async function login(page:Page) {
  await page.goto('/'); await page.getByLabel('Email').fill('bruno@workboard.test'); await page.getByLabel('Password').fill('bruno-passphrase-02'); await page.getByRole('button',{name:'Sign in',exact:true}).click(); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
}
test('late response from old list is ignored after ABA',async({page})=>{
  await login(page); const held=signal(), arrived=signal();
  await page.route('**/api/workspaces/ws_borealis/items', async route=>{const response=await route.fetch(); arrived.release(); await held.promise; await route.fulfill({response});},{times:1});
  await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_borealis'); await arrived.promise;
  await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_apollo'); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  const done=page.waitForResponse(r=>r.url().endsWith('/ws_borealis/items')); held.release(); await done;
  await expect(page.getByRole('heading',{name:'Update status page template'})).toHaveCount(0); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
});
test('membership loss is confirmed on retry before selecting first visible workspace',async({page})=>{
  await login(page);
  const db=new Database('data/e2e.sqlite'); const user=db.prepare('SELECT id FROM user WHERE email=?').get('bruno@workboard.test') as {id:string};
  const membership=db.prepare('SELECT * FROM membership WHERE userId=? AND workspaceId=?').get(user.id,'ws_borealis') as {workspaceId:string;userId:string;role:string;joinedAt:string};
  try {
    db.prepare('DELETE FROM membership WHERE userId=? AND workspaceId=?').run(user.id,'ws_borealis');
    await page.getByRole('combobox',{name:'Workspace',exact:true}).selectOption('ws_borealis'); await expect(page.getByRole('alert')).toContainText('Could not load work items'); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toHaveCount(0);
    await page.getByRole('button',{name:'Retry'}).click(); await expect(page.getByRole('combobox',{name:'Workspace',exact:true})).toHaveValue('ws_apollo'); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  } finally { db.prepare('INSERT INTO membership VALUES (?,?,?,?)').run(membership.workspaceId,membership.userId,membership.role,membership.joinedAt); db.close(); }
});
test('late success after closing form cannot affect a new form',async({page})=>{
  await login(page); const held=signal(), arrived=signal();
  await page.route('**/api/workspaces/ws_apollo/items',async route=>{if(route.request().method()!=='POST') return route.continue(); const response=await route.fetch(); arrived.release(); await held.promise; await route.fulfill({response});},{times:1});
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('Closed success'); await page.getByRole('button',{name:'Create work item'}).click(); await arrived.promise;
  await page.getByRole('button',{name:'Cancel',exact:true}).click(); await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('Another form');
  const done=page.waitForResponse(r=>r.url().endsWith('/ws_apollo/items') && r.request().method()==='POST'); held.release(); await done;
  await expect(page.getByLabel('Title')).toHaveValue('Another form'); await expect(page.getByText('Work item created.')).toHaveCount(0);
  const db=new Database('data/e2e.sqlite',{readonly:true}); expect(db.prepare('SELECT title FROM item WHERE title=?').get('Closed success')).toEqual({title:'Closed success'}); db.close();
});
