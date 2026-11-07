// REVIEW DIAGNOSTIC ONLY; static seed and cursor-model counterexample.
import Database from 'better-sqlite3';
import { SEED_ITEMS } from './server/seed.js';
const db = new Database(':memory:');
db.exec('CREATE TABLE i(id TEXT, workspace TEXT, title TEXT, status TEXT, created TEXT, updated TEXT)');
const insert = db.prepare('INSERT INTO i VALUES (?,?,?,?,?,?)');
for (const x of SEED_ITEMS) insert.run(x.id,x.workspaceId,x.title,x.status,x.createdAt,x.updatedAt);
for (const order of ['updated DESC,id ASC','updated ASC,id DESC','title COLLATE NOCASE ASC,id ASC','created ASC,id ASC']) {
  const rows = db.prepare(`SELECT id FROM i WHERE workspace=? ORDER BY ${order}`).all('ws_apollo');
  console.log(order, JSON.stringify(rows.map((x:any)=>x.id)));
}
console.log('status counts',JSON.stringify(db.prepare('SELECT workspace,status,count(*) n FROM i GROUP BY workspace,status ORDER BY workspace,status').all()));
db.exec('CREATE TABLE walk(id TEXT,updated TEXT)');
const add=db.prepare('INSERT INTO walk VALUES (?,?)');
const t='2026-11-07T12:00:00.000Z';
add.run('wi_a',t); add.run('wi_z_old','2026-11-07T11:59:59.999Z');
console.log('page1',JSON.stringify(db.prepare('SELECT * FROM walk ORDER BY updated DESC,id ASC LIMIT 1').all()));
add.run('wi_z_new',t);
console.log('page2_after_new_create_same_clock',JSON.stringify(db.prepare('SELECT * FROM walk WHERE updated < ? OR (updated = ? AND id > ?) ORDER BY updated DESC,id ASC LIMIT 2').all(t,t,'wi_a')));
db.close();
