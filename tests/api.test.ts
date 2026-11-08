import { beforeAll, afterAll, describe, expect, test } from 'vitest';
import { execFileSync } from 'node:child_process';
import { serve } from '@hono/node-server';
import Database from 'better-sqlite3';
import { dbPath, makeAuth, openDb } from '../server/db';
import { createApp, validateItem } from '../server/app';
type Server = ReturnType<typeof serve>;

let db:Database.Database, other:Database.Database, server:Server, base:string;
let ada:string, bruno:string, cleo:string;
async function req(path:string, method='GET', body?:unknown, cookie?:string) {
  return fetch(base+path,{ method, headers:{ ...(cookie ? {cookie}:{}), ...(body !== undefined ? {'content-type':'application/json'}:{}) }, ...(body !== undefined ? {body:typeof body === 'string' ? body : JSON.stringify(body)}:{}) });
}
async function signIn(email:string,password:string) {
  const res = await req('/api/auth/sign-in/email','POST',{email,password}); expect(res.status).toBe(200);
  const cookie = res.headers.getSetCookie().map(c=>c.split(';')[0]).join('; '); expect(cookie).toContain('session_token='); return cookie;
}
beforeAll(async()=>{
  process.env.WORKBOARD_DB='api-test.sqlite';
  execFileSync('npm',['run','reset'],{env:{...process.env},stdio:'pipe'});
  db=openDb(); other=new Database(dbPath()); const app=createApp(db,makeAuth(db));
  server=serve({fetch:app.fetch,port:0,hostname:'127.0.0.1'});
  await new Promise<void>(resolve=>server.once('listening',resolve));
  const address=server.address(); if (!address || typeof address === 'string') throw new Error('No port'); base=`http://127.0.0.1:${address.port}`;
  ada=await signIn('ada@workboard.test','ada-passphrase-01'); bruno=await signIn('bruno@workboard.test','bruno-passphrase-02'); cleo=await signIn('cleo@workboard.test','cleo-passphrase-03');
});
afterAll(async()=>{ await new Promise<void>(resolve=>server.close(()=>resolve())); other.close(); db.close(); });
describe('validation',()=>{
  test('exact field messages and shape-only dates',()=>{
    expect(validateItem({},true)).toEqual({title:'title is required.'});
    expect(validateItem({title:'',notes:4,status:'bad',dueDate:'2026-1-01'},true)).toEqual({title:'title must be a non-empty string.',notes:'notes must be a string.',status:'status must be one of: open, in_progress, done.',dueDate:'dueDate must be null or a YYYY-MM-DD string.'});
    expect(validateItem({title:' ',dueDate:'2026-99-99'},true)).toEqual({});
  });
});
describe('real HTTP, native sessions and SQLite',()=>{
  test('routing and visibility take precedence',async()=>{
    expect((await req('/api/absent')).status).toBe(404);
    expect(await (await req('/api/workspaces','PUT')).json()).toEqual({error:{code:'not_found',message:'Unknown API endpoint.'}});
    expect((await req('/api/workspaces/ws_apollo/items')).status).toBe(401);
    for (const path of ['/api/workspaces/ws_borealis','/api/workspaces/ws_borealis/items','/api/items/wi_202','/api/items/unknown']) {
      const r=await req(path,path.includes('/items/wi_')||path.endsWith('/unknown')?'PATCH':'GET',path.includes('/items/wi_')||path.endsWith('/unknown')?'broken':undefined,ada); expect(r.status).toBe(404);
    }
    expect((await req('/api/health')).status).toBe(200);
  });
  test('HEAD and native auth wire observations',async()=>{
    const health=await req('/api/health','HEAD'); expect(health.status).toBe(200); expect(await health.text()).toBe('');
    expect((await req('/api/me','HEAD')).status).toBe(401);
    expect((await req('/api/nope','HEAD')).status).toBe(404);
    expect((await req('/api/auth/get-session','HEAD')).status).toBe(404);
    const bad=await req('/api/auth/sign-in/email','POST',{email:'ada@workboard.test',password:'wrong'}); expect(bad.status).toBe(401); expect(await bad.json()).toEqual({message:'Invalid email or password',code:'INVALID_EMAIL_OR_PASSWORD'});
    expect((await req('/api/auth/sign-out','POST')).status).toBe(415);
    const ok=await req('/api/auth/sign-in/email','POST',{email:'ada@workboard.test',password:'ada-passphrase-01'});
    const cookie=ok.headers.getSetCookie()[0]; expect(cookie).toMatch(/^better-auth\.session_token=/); expect(cookie).toContain('HttpOnly'); expect(cookie).toContain('SameSite=Lax'); expect(cookie).toContain('Path=/');
  });
  test('seed and sorted membership across roles',async()=>{
    const me=await (await req('/api/me','GET',undefined,bruno)).json(); expect(me.workspaces.map((w:{id:string})=>w.id)).toEqual(['ws_apollo','ws_borealis']);
    const list=await (await req('/api/workspaces/ws_apollo/items','GET',undefined,ada)).json();
    expect(list.items.map((i:{id:string})=>i.id)).toEqual(['wi_103','wi_106','wi_104','wi_102','wi_107','wi_105','wi_101','wi_108']);
    expect(list.items.every((i:{notes:string;version:number})=>i.notes==='' && i.version===1)).toBe(true);
    expect((await req('/api/workspaces/ws_apollo','GET',undefined,cleo)).status).toBe(404);
    const rows=other.prepare('SELECT i.*,u.email FROM item i JOIN user u ON u.id=i.createdBy ORDER BY i.id').all();
    expect(rows).toHaveLength(13);
    expect(rows).toContainEqual({id:'wi_103',workspaceId:'ws_apollo',title:'Prepare demo script',notes:'',status:'open',dueDate:null,version:1,createdBy:me.user.id,createdAt:'2026-11-01T11:00:00.000Z',updatedAt:'2026-11-04T10:15:00.000Z',email:'bruno@workboard.test'});
    expect(other.prepare('SELECT workspaceId,role,joinedAt FROM membership WHERE userId=? ORDER BY workspaceId').all(me.user.id)).toEqual([{workspaceId:'ws_apollo',role:'member',joinedAt:'2026-10-21T09:00:00.000Z'},{workspaceId:'ws_borealis',role:'owner',joinedAt:'2026-10-25T09:00:00.000Z'}]);
  });
  test('malformed, non-object, exact errors and membership before validation',async()=>{
    for (const body of ['{', '[]','null']) { const r=await req('/api/workspaces/ws_apollo/items','POST',body,ada); expect(r.status).toBe(400); expect(await r.json()).toEqual({error:{code:'validation_failed',message:'request body must be valid JSON.'}}); }
    const r=await req('/api/workspaces/ws_apollo/items','POST',{},ada); expect(await r.json()).toEqual({error:{code:'validation_failed',message:'Invalid work item input.',fields:{title:'title is required.'}}});
    expect((await req('/api/workspaces/ws_borealis/items','POST','{',ada)).status).toBe(404);
  });
  test('member CRUD, last-write-wins and separate connection',async()=>{
    const created=await req('/api/workspaces/ws_apollo/items','POST',{title:'  verbatim  ',notes:'line\n2',dueDate:'2026-99-99',ignored:1},bruno); expect(created.status).toBe(201);
    const i=await created.json(); expect(i.id).toMatch(/^wi_[0-9a-f]{20}$/); expect(i).toMatchObject({title:'  verbatim  ',notes:'line\n2',status:'open',dueDate:'2026-99-99',version:1});
    expect(other.prepare('SELECT title,version FROM item WHERE id=?').get(i.id)).toEqual({title:'  verbatim  ',version:1});
    expect((await req(`/api/items/${i.id}`,'PATCH',{ignored:1},ada)).status).toBe(400);
    expect((await (await req(`/api/items/${i.id}`,'PATCH',{title:'first',version:1},ada)).json()).version).toBe(2);
    const last=await (await req(`/api/items/${i.id}`,'PATCH',{title:'second',dueDate:null,version:1},bruno)).json(); expect(last).toMatchObject({title:'second',dueDate:null,version:3});
    expect(other.prepare('SELECT title,version,dueDate FROM item WHERE id=?').get(i.id)).toEqual({title:'second',version:3,dueDate:null});
    const del=await req(`/api/items/${i.id}`,'DELETE',undefined,ada); expect(del.status).toBe(204); expect(await del.text()).toBe(''); expect(other.prepare('SELECT id FROM item WHERE id=?').get(i.id)).toBeUndefined();
  });

  test('workspace summaries openItemCount',async()=>{
    const me = await (await req('/api/me','GET',undefined,bruno)).json();
    const summaries = me.workspaces;
    const apollo = summaries.find((w:{id:string})=>w.id==='ws_apollo');
    const borealis = summaries.find((w:{id:string})=>w.id==='ws_borealis');
    expect(apollo?.openItemCount).toBe(4);
    expect(borealis?.openItemCount).toBe(3);

    const list = await (await req('/api/workspaces','GET',undefined,bruno)).json();
    expect(list).toEqual(summaries);

    const cleoMe = await (await req('/api/me','GET',undefined,cleo)).json();
    expect(cleoMe.workspaces).toEqual([
      expect.objectContaining({ id: 'ws_borealis', openItemCount: 3 })
    ]);

    const newItem = { title: 'Temp Item' };
    const created = await req('/api/workspaces/ws_apollo/items','POST',newItem,bruno);
    const i = await created.json();

    const meAfter = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(meAfter.workspaces.find((w:{id:string})=>w.id==='ws_apollo')?.openItemCount).toBe(5);
    expect(meAfter.workspaces.find((w:{id:string})=>w.id==='ws_borealis')?.openItemCount).toBe(3);

    await req(`/api/items/${i.id}`,'PATCH',{status:'done'},bruno);
    const meDone = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(meDone.workspaces.find((w:{id:string})=>w.id==='ws_apollo')?.openItemCount).toBe(4);

    await req(`/api/items/${i.id}`,'DELETE',undefined,bruno);
    const meDel = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(meDel.workspaces.find((w:{id:string})=>w.id==='ws_apollo')?.openItemCount).toBe(4);
  });
  test('signup, workspace ownership, duplicate membership sets and signout',async()=>{
    const signup=await req('/api/auth/sign-up/email','POST',{name:'New User',email:'new@workboard.test',password:'password-123'}); expect(signup.status).toBe(200);
    const cookie=signup.headers.getSetCookie().map(c=>c.split(';')[0]).join('; '); expect(cookie).toContain('session_token=');
    const before=await (await req('/api/me','GET',undefined,cookie)).json(); expect(before.workspaces).toEqual([]);
    const a=await (await req('/api/workspaces','POST',{name:'Same'},cookie)).json(); const b=await (await req('/api/workspaces','POST',{name:'Same'},cookie)).json();
    expect(a.id).toMatch(/^ws_[0-9a-f]{20}$/); expect(a.id).not.toBe(b.id); expect(a.role).toBe('owner');
    expect(other.prepare('SELECT count(*) n FROM membership WHERE userId=?').get(before.user.id)).toEqual({n:2});
    const out=await req('/api/auth/sign-out','POST',{},cookie); expect(out.status).toBe(200); expect(out.headers.getSetCookie()[0]).toContain('Max-Age=0'); expect((await req('/api/me','GET',undefined,cookie)).status).toBe(401);
  });
});
