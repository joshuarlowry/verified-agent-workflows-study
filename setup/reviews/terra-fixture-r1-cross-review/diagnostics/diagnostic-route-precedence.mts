// REVIEW DIAGNOSTIC ONLY; not part of the fixture.
import { createTestApp } from './tests/api/helpers.js';
const t = await createTestApp('r1-route-probe');
try {
  for (const [method,path] of [['HEAD','/api/me'],['HEAD','/api/health'],['POST','/api/health'],['GET','/api/auth/no-such-route'],['DELETE','/api/auth/no-such-route']]) {
    const r = await t.request(path,{method});
    console.log(method,path,r.status,await r.text());
  }
} finally { t.close(); }
