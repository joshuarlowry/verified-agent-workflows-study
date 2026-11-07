import { serve } from '@hono/node-server';
import { openDb, makeAuth } from './db';
import { createApp } from './app';

const db = openDb();
if (!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='membership'").get()) { db.close(); throw new Error('Database is not initialized; run npm run reset first.'); }
const auth = makeAuth(db);
const app = createApp(db,auth);
const port = Number(process.env.PORT || 3000);
const server = serve({ fetch: app.fetch, port, hostname:'127.0.0.1' }, info => console.log(`Workboard listening at http://localhost:${info.port}`));
for (const signal of ['SIGINT','SIGTERM'] as const) process.on(signal, () => server.close(() => { db.close(); process.exit(0); }));
