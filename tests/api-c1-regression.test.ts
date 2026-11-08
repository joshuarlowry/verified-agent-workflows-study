import { beforeAll, afterAll, describe, expect, test } from 'vitest';
import { execFileSync } from 'node:child_process';
import { serve } from '@hono/node-server';
import Database from 'better-sqlite3';
import { dbPath, makeAuth, openDb } from '../server/db';
import { createApp } from '../server/app';
type Server = ReturnType<typeof serve>;

let db:Database.Database, other:Database.Database, server:Server, base:string;
let bruno:string;
async function req(path:string, method='GET', body?:unknown, cookie?:string) {
  return fetch(base+path,{ method, headers:{ ...(cookie ? {cookie}:{}), ...(body !== undefined ? {'content-type':'application/json'}:{}) }, ...(body !== undefined ? {body:typeof body === 'string' ? body : JSON.stringify(body)}:{}) });
}
async function signIn(email:string,password:string) {
  const res = await req('/api/auth/sign-in/email','POST',{email,password}); expect(res.status).toBe(200);
  const cookie = res.headers.getSetCookie().map(c=>c.split(';')[0]).join('; '); expect(cookie).toContain('session_token='); return cookie;
}
beforeAll(async()=>{
  process.env.WORKBOARD_DB='api-test-c1-reg.sqlite';
  execFileSync('npm',['run','reset'],{env:{...process.env},stdio:'pipe'});
  db=openDb(); other=new Database(dbPath()); const app=createApp(db,makeAuth(db));
  server=serve({fetch:app.fetch,port:0,hostname:'127.0.0.1'});
  await new Promise<void>(resolve=>server.once('listening',resolve));
  const address=server.address(); if (!address || typeof address === 'string') throw new Error('No port'); base=`http://127.0.0.1:${address.port}`;
  bruno=await signIn('bruno@workboard.test','bruno-passphrase-02');
});
afterAll(async()=>{ await new Promise<void>(resolve=>server.close(()=>resolve())); other.close(); db.close(); });

describe('C1 - Workspace item counts regression',()=>{
  test('summary endpoints include openItemCount',async()=>{
    const me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    expect(me.workspaces[0]).toHaveProperty('openItemCount');
    
    const list = await (await req('/api/workspaces','GET',undefined,bruno)).json() as any[];
    expect(list[0]).toHaveProperty('openItemCount');
  });

  test('seed counts are correct',async()=>{
    const me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    const apollo = me.workspaces.find((w:any)=>w.id==='ws_apollo');
    const borealis = me.workspaces.find((w:any)=>w.id==='ws_borealis');
    expect(apollo?.openItemCount).toBe(4);
    expect(borealis?.openItemCount).toBe(3);
  });

  test('item operations update count dynamically',async()=>{
    const wsId = 'ws_apollo';
    // 1. Create open item
    await req(`/api/workspaces/${wsId}/items`,'POST',{title:'Dynamic Open'},bruno);
    let me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    expect(me.workspaces.find((w:any)=>w.id===wsId)?.openItemCount).toBe(5);

    // 2. Create non-open item
    await req(`/api/workspaces/${wsId}/items`,'POST',{title:'Dynamic Done', status:'done'},bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    expect(me.workspaces.find((w:any)=>w.id===wsId)?.openItemCount).toBe(5);

    // 3. Transition open to done
    const items = await (await req(`/api/workspaces/${wsId}/items`,'GET',undefined,bruno)).json() as any;
    const openItem = items.items.find((i:any)=>i.title==='Dynamic Open');
    await req(`/api/items/${openItem.id}`,'PATCH',{status:'done'},bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    expect(me.workspaces.find((w:any)=>w.id===wsId)?.openItemCount).toBe(4);

    // 4. Delete open item
    const items2 = await (await req(`/api/workspaces/${wsId}/items`,'GET',undefined,bruno)).json() as any;
    const otherOpen = items2.items.find((i:any)=>i.status==='open');
    await req(`/api/items/${otherOpen.id}`,'DELETE',undefined,bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json() as any;
    expect(me.workspaces.find((w:any)=>w.id===wsId)?.openItemCount).toBe(3);
  });

  test('workspace detail shape preserves no count',async()=>{
    const detail = await (await req('/api/workspaces/ws_apollo','GET',undefined,bruno)).json() as any;
    expect(detail.openItemCount).toBeUndefined();
  });

  test('user visibility and isolation',async()=>{
    const cleo = await signIn('cleo@workboard.test','cleo-passphrase-03');
    const me = await (await req('/api/me','GET',undefined,cleo)).json() as any;
    // Cleo is only in Borealis
    expect(me.workspaces).toHaveLength(1);
    expect(me.workspaces[0].id).toBe('ws_borealis');
    expect(me.workspaces[0].openItemCount).toBe(3);
  });
});
