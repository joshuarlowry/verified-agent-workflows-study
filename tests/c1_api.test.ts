import { beforeAll, afterAll, describe, expect, test } from 'vitest';
import { execFileSync } from 'node:child_process';
import { serve } from '@hono/node-server';
import Database from 'better-sqlite3';
import { makeAuth, openDb } from '../server/db';
import { createApp } from '../server/app';
type Server = ReturnType<typeof serve>;

let db:Database.Database, server:Server, base:string;

async function req(path:string, method='GET', body?:unknown, cookie?:string) {
  return fetch(base+path,{ method, headers:{ ...(cookie ? {cookie}:{}), ...(body !== undefined ? {'content-type':'application/json'}:{}) }, ...(body !== undefined ? {body:typeof body === 'string' ? body : JSON.stringify(body)}:{}) });
}
async function signIn(email:string,password:string) {
  const res = await req('/api/auth/sign-in/email','POST',{email,password}); expect(res.status).toBe(200);
  const cookie = res.headers.getSetCookie().map(c=>c.split(';')[0]).join('; '); return cookie;
}
beforeAll(async()=>{
  process.env.WORKBOARD_DB='api-test-c1-new.sqlite';
  execFileSync('npm',['run','reset'],{env:{...process.env},stdio:'pipe'});
  db=openDb(); const app=createApp(db,makeAuth(db));
  server=serve({fetch:app.fetch,port:0,hostname:'127.0.0.1'});
  await new Promise<void>(resolve=>server.once('listening',resolve));
  const address=server.address(); if (!address || typeof address === 'string') throw new Error('No port'); base=`http://127.0.0.1:${address.port}`;
});
afterAll(async()=>{ await new Promise<void>(resolve=>server.close(()=>resolve())); db.close(); });

describe('C1 Workspace Item Counts', () => {
  test('seeded counts are exact 4/3', async () => {
    const bruno = await signIn('bruno@workboard.test','bruno-passphrase-02');
    const me = await (await req('/api/me','GET',undefined,bruno)).json();
    const apollo = me.workspaces.find((w:any)=>w.id === 'ws_apollo');
    const borealis = me.workspaces.find((w:any)=>w.id === 'ws_borealis');
    expect(apollo.openItemCount).toBe(4);
    expect(borealis.openItemCount).toBe(3);
  });

  test('counts across both summary endpoints', async () => {
    const bruno = await signIn('bruno@workboard.test','bruno-passphrase-02');
    const me = await (await req('/api/me','GET',undefined,bruno)).json();
    const ws = await (await req('/api/workspaces','GET',undefined,bruno)).json();
    expect(me.workspaces[0].openItemCount).toBe(ws[0].openItemCount);
  });

  test('status transitions and non-open items', async () => {
    const bruno = await signIn('bruno@workboard.test','bruno-passphrase-02');
    const item = await (await req('/api/workspaces/ws_apollo/items','POST',{title:'Count Test'},bruno)).json();
    let me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(5);

    await req(`/api/items/${item.id}`,'PATCH',{status:'in_progress'},bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(4);

    await req(`/api/items/${item.id}`,'PATCH',{status:'open'},bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(5);

    await req(`/api/items/${item.id}`,'PATCH',{status:'done'},bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(4);

    // cleanup
    await req(`/api/items/${item.id}`,'DELETE',undefined,bruno);
  });

  test('deletion decreases count', async () => {
    const bruno = await signIn('bruno@workboard.test','bruno-passphrase-02');
    const item = await (await req('/api/workspaces/ws_apollo/items','POST',{title:'Delete Test'},bruno)).json();
    let me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(5);
    
    await req(`/api/items/${item.id}`,'DELETE',undefined,bruno);
    me = await (await req('/api/me','GET',undefined,bruno)).json();
    expect(me.workspaces.find((w:any)=>w.id === 'ws_apollo').openItemCount).toBe(4);
  });

  test('visibility and roles', async () => {
    const cleo = await signIn('cleo@workboard.test','cleo-passphrase-03');
    const meCleo = await (await req('/api/me','GET',undefined,cleo)).json();
    expect(meCleo.workspaces.find((w:any)=>w.id === 'ws_apollo')).toBeUndefined();
    expect(meCleo.workspaces.find((w:any)=>w.id === 'ws_borealis').openItemCount).toBe(3);
  });

  test('detail shape and zero count', async () => {
    const signup = await req('/api/auth/sign-up/email','POST',{name:'New C1',email:'new-c1@workboard.test',password:'password-123'});
    const cookieNew = signup.headers.getSetCookie().map(c=>c.split(';')[0]).join('; ');

    const wsDetail = await (await req('/api/workspaces','POST',{name:'Empty'},cookieNew)).json();
    expect(wsDetail.openItemCount).toBeUndefined();

    const me = await (await req('/api/me','GET',undefined,cookieNew)).json();
    const summary = me.workspaces.find((w:any)=>w.name === 'Empty');
    expect(summary.openItemCount).toBe(0);
  });
});
