import { Hono, type Context } from 'hono';
import { serveStatic } from '@hono/node-server/serve-static';
import { randomBytes } from 'node:crypto';
import type Database from 'better-sqlite3';
import type { makeAuth } from './db';

const now = () => new Date().toISOString();
const id = (prefix: string) => `${prefix}_${randomBytes(10).toString('hex')}`;
const error = (c: Context, status: 400|401|404|500, code: string, message: string, fields?: Record<string,string>) => c.json({ error: { code, message, ...(fields ? { fields } : {}) } }, status);
const notFound = (c: Context) => error(c,404,'not_found','Not found.');
const unknown = (c: Context) => error(c,404,'not_found','Unknown API endpoint.');
export function validateItem(body: Record<string, unknown>, create: boolean) {
  const fields: Record<string, string> = {};
  if (create && !('title' in body)) fields.title = 'title is required.';
  else if ('title' in body && (typeof body.title !== 'string' || body.title.length === 0)) fields.title = 'title must be a non-empty string.';
  if ('notes' in body && typeof body.notes !== 'string') fields.notes = 'notes must be a string.';
  if ('status' in body && !['open','in_progress','done'].includes(body.status as string)) fields.status = 'status must be one of: open, in_progress, done.';
  if ('dueDate' in body && body.dueDate !== null && (typeof body.dueDate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(body.dueDate))) fields.dueDate = 'dueDate must be null or a YYYY-MM-DD string.';
  return fields;
}
async function bodyObject(c: Context): Promise<Record<string,unknown> | null> {
  try { const value: unknown = await c.req.json(); return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string,unknown> : null; } catch { return null; }
}
const badBody = (c: Context) => error(c,400,'validation_failed','request body must be valid JSON.');

type Item = { id:string; workspaceId:string; title:string; notes:string; status:string; dueDate:string|null; version:number; createdBy:string; createdAt:string; updatedAt:string };
type Workspace = { id:string; name:string; role:string; createdAt:string; updatedAt:string };
export function createApp(db: Database.Database, auth: ReturnType<typeof makeAuth>) {
  const app = new Hono();
  const summaries = (uid: string) => db.prepare(`SELECT w.id,w.name,m.role,w.createdAt,
    (SELECT count(*) FROM item i WHERE i.workspaceId=w.id AND i.status='open') AS openItemCount
    FROM workspace w JOIN membership m ON m.workspaceId=w.id WHERE m.userId=?
    ORDER BY w.name COLLATE BINARY, w.createdAt, w.id COLLATE BINARY`).all(uid);
  const workspace = (ws: string, uid: string) => db.prepare('SELECT w.*,m.role FROM workspace w JOIN membership m ON m.workspaceId=w.id WHERE w.id=? AND m.userId=?').get(ws,uid) as Workspace|undefined;
  const item = (itemId: string, uid: string) => db.prepare('SELECT i.* FROM item i JOIN membership m ON m.workspaceId=i.workspaceId WHERE i.id=? AND m.userId=?').get(itemId,uid) as Item|undefined;
  const user = async (c: Context) => (await auth.api.getSession({ headers:c.req.raw.headers }))?.user;
  app.get('/api/health', c => c.json({ok:true,name:'workboard-lab',schemaVersion:1,time:now()}));
  app.on(['GET','POST'],'/api/auth/*', c => auth.handler(c.req.raw));
  app.get('/api/me', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    return c.json({ user: { id:u.id,email:u.email,name:u.name }, workspaces:summaries(u.id) });
  });
  app.get('/api/workspaces', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    return c.json(summaries(u.id));
  });
  app.post('/api/workspaces', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const body = await bodyObject(c); if (!body) return badBody(c);
    if (typeof body.name !== 'string' || !body.name.length) return error(c,400,'validation_failed','Invalid workspace input.',{name:'name must be a non-empty string.'});
    const ws = id('ws'), t = now();
    db.transaction(() => { db.prepare('INSERT INTO workspace VALUES (?,?,?,?)').run(ws,body.name,t,t); db.prepare('INSERT INTO membership VALUES (?,?,?,?)').run(ws,u.id,'owner',t); })();
    return c.json(workspace(ws,u.id),201);
  });
  app.get('/api/workspaces/:id', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const ws = workspace(c.req.param('id'),u.id); if (!ws) return notFound(c);
    return c.json(ws);
  });
  app.get('/api/workspaces/:id/items', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const ws = workspace(c.req.param('id'),u.id); if (!ws) return notFound(c);
    return c.json({ workspaceId:ws.id, items:db.prepare('SELECT * FROM item WHERE workspaceId=? ORDER BY updatedAt DESC,id COLLATE BINARY ASC').all(ws.id) });
  });
  app.post('/api/workspaces/:id/items', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const ws = workspace(c.req.param('id'),u.id); if (!ws) return notFound(c);
    const body = await bodyObject(c); if (!body) return badBody(c);
    const fields = validateItem(body,true); if (Object.keys(fields).length) return error(c,400,'validation_failed','Invalid work item input.',fields);
    const itemId = id('wi'), t = now();
    db.prepare('INSERT INTO item VALUES (?,?,?,?,?,?,?,?,?,?)').run(itemId,ws.id,body.title,body.notes ?? '',body.status ?? 'open',body.dueDate ?? null,1,u.id,t,t);
    return c.json(item(itemId,u.id),201);
  });
  app.patch('/api/items/:id', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const current = item(c.req.param('id'),u.id); if (!current) return notFound(c);
    const body = await bodyObject(c); if (!body) return badBody(c);
    const fields = validateItem(body,false); if (Object.keys(fields).length) return error(c,400,'validation_failed','Invalid work item input.',fields);
    if (!['title','notes','status','dueDate'].some(k => k in body)) return error(c,400,'validation_failed','Invalid work item input.');
    db.prepare('UPDATE item SET title=?,notes=?,status=?,dueDate=?,version=version+1,updatedAt=? WHERE id=?').run(body.title ?? current.title,body.notes ?? current.notes,body.status ?? current.status,'dueDate' in body ? body.dueDate : current.dueDate,now(),current.id);
    return c.json(item(current.id,u.id));
  });
  app.delete('/api/items/:id', async c => {
    const u = await user(c); if (!u) return error(c,401,'unauthenticated','Authentication required.');
    const current = item(c.req.param('id'),u.id); if (!current) return notFound(c);
    db.prepare('DELETE FROM item WHERE id=?').run(current.id);
    return c.body(null,204);
  });
  app.all('/api/*', unknown);
  app.use('/*', serveStatic({ root:'./dist' }));
  app.get('*', serveStatic({ path:'./dist/index.html' }));
  app.notFound(unknown);
  app.onError((e,c) => { console.error(e); return error(c,500,'internal_error','Internal server error.'); });
  return app;
}
