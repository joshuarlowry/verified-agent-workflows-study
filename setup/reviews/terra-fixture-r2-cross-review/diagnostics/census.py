#!/usr/bin/env python3
# Review-authored static census; not acceptance tests.
import re,pathlib,json,hashlib
base=pathlib.Path('/workspace/inputs/fixture/baseline/e2e')
for file in ['ownership.spec.ts','switch.spec.ts']:
 s=(base/file).read_text()
 for label in ['Borealis Ops','Apollo Launch']:
  occ=[s.count('\n',0,m.start())+1 for m in re.finditer(r'selectOption\(\{\s*label:\s*"'+re.escape(label)+r'"\s*\}\)',s)]
  print(file, label, len(occ), occ)
for p in base.glob('*.ts'):
 for i,line in enumerate(p.read_text().splitlines(),1):
  if re.search(r'getByText\(["\'](?:Due |No due date)',line): print('due assertion',p.name,i,line.strip())
root=pathlib.Path('/workspace/inputs/fixture')
d=json.loads((root/'r2-endpoint-manifest.json').read_text())
h=hashlib.sha256(json.dumps(d['source_files'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
print('inner manifest entries:',len(d['source_files']),'array hash:',h,'declared:',d.get('tree_sha256'))
print('inner entries differing from actual:',[x['path'] for x in d['source_files'] if not (root/x['path']).is_file() or hashlib.sha256((root/x['path']).read_bytes()).hexdigest()!=x['sha256'] or (root/x['path']).stat().st_size!=x['bytes']])
