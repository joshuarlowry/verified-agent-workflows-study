#!/usr/bin/env python3
# Review-authored source identity diagnostic; read-only, not an acceptance fixture.
import hashlib,json,pathlib,sys
root=pathlib.Path('/workspace/inputs/fixture')
m=pathlib.Path('/workspace/inputs/endpoint-manifest.json')
r=pathlib.Path('/workspace/inputs/prior-review.json')
d=json.loads(m.read_text()); entries=d['source_files']; seen=set(); errors=[]
def sha(b): return hashlib.sha256(b).hexdigest()
for x in entries:
 p=x['path']; f=root/p
 if p in seen: errors.append('duplicate '+p)
 seen.add(p)
 if not f.is_file() or f.is_symlink(): errors.append('not regular '+p); continue
 b=f.read_bytes()
 if len(b)!=x['bytes'] or sha(b)!=x['sha256']: errors.append('mismatch '+p)
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
errors += ['missing '+p for p in sorted(seen-actual)] + ['extra '+p for p in sorted(actual-seen)]
canonical=sha(json.dumps(entries,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
if canonical!=d['tree_sha256']: errors.append('canonical mismatch')
independent=sha(b''.join(p.encode()+b'\0'+sha((root/p).read_bytes()).encode()+b'\n' for p in sorted(actual)))
print('manifest_sha256',sha(m.read_bytes()))
print('prior_review_sha256',sha(r.read_bytes()))
print('count',len(entries),'actual',len(actual),'canonical',canonical,'independent',independent)
print('errors',errors)
for p in sorted(actual): print(sha((root/p).read_bytes()),p)
sys.exit(bool(errors))
