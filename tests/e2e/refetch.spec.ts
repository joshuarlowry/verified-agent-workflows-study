import { test, expect } from '@playwright/test';
const signal=()=>{let release!:()=>void; const promise=new Promise<void>(r=>{release=r;}); return {release,promise};};
test('a delayed save-triggered refetch cannot change a newly opened form or list',async({page})=>{
  await page.goto('/'); await page.getByLabel('Email').fill('bruno@workboard.test'); await page.getByLabel('Password').fill('bruno-passphrase-02'); await page.getByRole('button',{name:'Sign in',exact:true}).click(); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
  const arrived=signal(), held=signal();
  await page.route('**/api/workspaces/ws_apollo/items',async route=>{
    if(route.request().method()!=='GET') return route.continue();
    const response=await route.fetch(); arrived.release(); await held.promise;
    const body=await response.json(); body.items=[]; await route.fulfill({response,json:body});
  });
  await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('Refetch source'); await page.getByRole('button',{name:'Create work item'}).click(); await arrived.promise;
  await expect(page.getByText('Work item created.')).toBeVisible(); await page.getByRole('button',{name:'New work item'}).click(); await page.getByLabel('Title').fill('New form');
  const complete=page.waitForResponse(r=>r.url().endsWith('/ws_apollo/items') && r.request().method()==='GET'); held.release(); await complete;
  await expect(page.getByLabel('Title')).toHaveValue('New form'); await expect(page.getByRole('heading',{name:'Prepare demo script'})).toBeVisible();
});
