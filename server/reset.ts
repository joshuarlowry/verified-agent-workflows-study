import { rmSync, lstatSync } from 'node:fs';
import { dbPath, openDb, migrate } from './db';

const path = dbPath();
for (const suffix of ['', '-wal', '-shm']) {
  const file = path + suffix;
  if (lstatSync(file, {throwIfNoEntry:false})?.isSymbolicLink()) throw new Error('refusing to reset a symlink');
  rmSync(file, { force: true });
}
const db = openDb();
const auth = await migrate(db);
const users = [
  ['Ada Streams', 'ada@workboard.test', 'ada-passphrase-01'],
  ['Bruno Calder', 'bruno@workboard.test', 'bruno-passphrase-02'],
  ['Cleo Marsh', 'cleo@workboard.test', 'cleo-passphrase-03']
];
const ids: string[] = [];
for (const [name, email, password] of users) {
  const result = await auth.api.signUpEmail({ body: { name, email, password } });
  ids.push(result.user.id);
}
const workspaces = [ ['ws_apollo', 'Apollo Launch', '2026-10-20T09:00:00.000Z'], ['ws_borealis', 'Borealis Ops', '2026-10-25T09:00:00.000Z'] ];
const memberships: [string, number, string, string][] = [
 ['ws_apollo',0,'owner','2026-10-20T09:00:00.000Z'], ['ws_apollo',1,'member','2026-10-21T09:00:00.000Z'],
 ['ws_borealis',1,'owner','2026-10-25T09:00:00.000Z'], ['ws_borealis',2,'member','2026-10-26T09:00:00.000Z']
];
const items: [string,string,string,string,string|null,number,string,string][] = [
 ['wi_103','ws_apollo','Prepare demo script','open',null,1,'11:00','2026-11-04T10:15:00.000Z'],
 ['wi_106','ws_apollo','Fix mobile nav overflow','in_progress',null,0,'11:30','2026-11-04T09:00:00.000Z'],
 ['wi_104','ws_apollo','Ship onboarding email','done',null,1,'10:30','2026-11-03T16:40:00.000Z'],
 ['wi_102','ws_apollo','Review pricing copy','in_progress','2026-11-05',1,'10:00','2026-11-03T11:30:00.000Z'],
 ['wi_107','ws_apollo','Write release notes','open','2026-11-20',0,'10:15','2026-11-02T15:05:00.000Z'],
 ['wi_105','ws_apollo','Audit analytics events','open','2026-12-01',1,'10:45','2026-11-02T10:00:00.000Z'],
 ['wi_101','ws_apollo','Draft launch checklist','open','2026-11-12',0,'09:10','2026-11-01T14:20:00.000Z'],
 ['wi_108','ws_apollo','Archive old assets','done',null,1,'09:20','2026-11-01T09:30:00.000Z'],
 ['wi_202','ws_borealis','Update status page template','in_progress',null,1,'10:55','2026-11-04T08:45:00.000Z'],
 ['wi_205','ws_borealis','Draft vendor renewal memo','open','2026-11-28',1,'11:45','2026-11-03T13:10:00.000Z'],
 ['wi_201','ws_borealis','Rotate API keys','open','2026-11-15',1,'10:05','2026-11-02T09:15:00.000Z'],
 ['wi_203','ws_borealis','Quarterly access review','open',null,2,'09:05','2026-11-01T16:00:00.000Z'],
 ['wi_204','ws_borealis','Patch VPN gateway','done',null,1,'09:40','2026-11-01T10:45:00.000Z']
];
db.transaction(() => {
 for (const [id,name,t] of workspaces) db.prepare('INSERT INTO workspace VALUES (?,?,?,?)').run(id,name,t,t);
 for (const [ws,user,role,joined] of memberships) db.prepare('INSERT INTO membership VALUES (?,?,?,?)').run(ws,ids[user],role,joined);
 for (const [id,ws,title,status,due,user,created,updated] of items) db.prepare('INSERT INTO item VALUES (?,?,?,?,?,?,?,?,?,?)').run(id,ws,title,'',status,due,1,ids[user],`2026-11-01T${created}:00.000Z`,updated);
})();
db.close();
console.log(`Reset disposable database ${path}`);
