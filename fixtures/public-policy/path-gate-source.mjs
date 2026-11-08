#!/usr/bin/env node
// Finite fail-closed core source inventory; never imports subject code.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {preserveOriginalTest} from './preserve-tests.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(here);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const snapshot=JSON.parse(fs.readFileSync(path.join(here,'baseline-snapshot.json'))).files_sha256;
const protectedBundle=JSON.parse(fs.readFileSync(path.join(here,'protected-bundle.json'))).files_sha256;
function tree(dir) {
  const out={};
  function visit(prefix='') {
    for(const d of fs.readdirSync(path.join(dir,prefix),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) {
      const p=prefix ? `${prefix}/${d.name}` : d.name;
      if(d.isSymbolicLink()) throw Error(`symlink: ${p}`);
      if(d.isDirectory()) visit(p); else if(d.isFile()) out[p]=sha(fs.readFileSync(path.join(dir,p))); else throw Error(`nonregular: ${p}`);
    }
  }
  visit(); return out;
}
const keys=o=>Object.keys(o).sort();
function same(a,b) { return JSON.stringify(keys(a))===JSON.stringify(keys(b)) && keys(a).every(k=>a[k]===b[k]); }
function checkProtected() {
  for(const [p,hash] of Object.entries(protectedBundle)) {
    if(!/^(tests\/|helpers\/|fixtures\/html\/|materials\/|playwright\.config\.ts$|package(?:-lock)?\.json$|tsconfig\.json$|db-scope\/)/.test(p) || p.includes('..')) throw Error(`invalid protected entry ${p}`);
    const file=path.join(root,p); if(!fs.lstatSync(file).isFile() || sha(fs.readFileSync(file))!==hash) throw Error(`protected bundle mismatch ${p}`);
  }
}
try {
  const [base,target,...extra]=process.argv.slice(2); if(!base || !target || extra.length) throw Error('usage: node core.mjs BASE TARGET');
  checkProtected(); const b=tree(base), t=tree(target); if(!same(b,snapshot)) throw Error('baseline tree differs from frozen snapshot');
  const changes=[...new Set([...keys(b),...keys(t)])].sort().filter(p=>b[p]!==t[p]).map(p=>({path:p,before:b[p]??null,after:t[p]??null}));
  const test_preservation=[];
  for(const c of changes) {
    const p=c.path;
    if(p.startsWith('tests/') && c.before) {
      if(c.after===null) throw Error(`original test deletion: ${p}`);
      const result=preserveOriginalTest(p,fs.readFileSync(path.join(base,p),'utf8'),fs.readFileSync(path.join(target,p),'utf8'));
      test_preservation.push({path:p,...result});
      continue;
    }
    if(c.after===null) throw Error(`baseline source deletion unsupported: ${p}`);
    const existing=['server/app.ts','server/db.ts','src/main.tsx','src/style.css'].includes(p);
    const added=!(p in b) && (/^(src|server)\/[A-Za-z0-9_./-]+\.(ts|tsx|css)$/.test(p) || /^tests\/[A-Za-z0-9_./-]+\.(ts|tsx|js|jsx|css)$/.test(p));
    if(!existing && !added) throw Error(`protected or unsupported path: ${p}`);
  }
  console.log(JSON.stringify({status:'verified_finite_source_inventory',patch_sha256:sha(JSON.stringify(changes)),protected_bundle_sha256:sha(fs.readFileSync(path.join(here,'protected-bundle.json'))),changes,test_preservation,limitations:['No semantic equivalence proof','Original test transformations outside the finite preservation rule and dependency changes are unsupported','Subject source inside permitted paths not semantically verified']},null,2));
} catch(e) { console.error(JSON.stringify({status:'violation_or_unverified',error:e.message})); process.exitCode=1; }
