// C1 finite original-test preservation rule. No subject module is imported.
import ts from 'typescript';

if (ts.version !== '5.9.3') throw Error(`requires trusted TypeScript 5.9.3, got ${ts.version}`);

const OLD = "expect(me.workspaces.map((w:{id:string})=>w.id)).toEqual(['ws_apollo','ws_borealis']);";
const MIGRATED = "expect(me.workspaces.map((w:{id:string;openItemCount:number})=>({id:w.id,openItemCount:w.openItemCount}))).toEqual([{id:'ws_apollo',openItemCount:4},{id:'ws_borealis',openItemCount:3}]);";
const seedTitle = 'seed and sorted membership across roles';
const assertion = /^expect\(me\.workspaces(?:\.length|\[[01]\]\.openItemCount)\)\.toBe\((?:0|[1-9][0-9]{0,5})\);$/;
// A deliberately small read-only new-case DSL; no imports, hooks or arbitrary expressions.
const newCase = /^test\('[A-Za-z0-9 _-]{1,80}', async \(\) => \{\n  const response = await req\('\/api\/me', 'GET', undefined, bruno\);\n  expect\(response\.status\)\.toBe\(200\);\n  const body = await response\.json\(\);\n(?:  expect\(body\.workspaces(?:\.length|\[[01]\]\.openItemCount)\)\.toBe\((?:0|[1-9][0-9]{0,5})\);\n){1,16}\}\);$/;

function parse(text, name) {
  const sf = ts.createSourceFile(name, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  if (sf.parseDiagnostics.length) throw Error(`test syntax error: ${name}`);
  return sf;
}
function testCall(node) {
  return ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'test' && node.arguments.length === 2 && ts.isStringLiteral(node.arguments[0]) && ts.isArrowFunction(node.arguments[1]) && ts.isBlock(node.arguments[1].body);
}
function findSeed(sf) {
  const found=[];
  function visit(n) { if (testCall(n) && n.arguments[0].text === seedTitle) found.push(n); ts.forEachChild(n,visit); }
  visit(sf);
  if (found.length !== 1) throw Error('seed test missing or duplicated');
  return found[0].arguments[1].body;
}
function count(text, needle) { return text.split(needle).length - 1; }

// Only direct, ordinary describe callbacks at source level or inside another
// such callback are eligible. Never traverse test bodies or arbitrary blocks.
function groupCall(stmt) {
  if (!ts.isExpressionStatement(stmt) || !ts.isCallExpression(stmt.expression)) return null;
  const call=stmt.expression;
  if (!ts.isIdentifier(call.expression) || call.expression.text !== 'describe' || call.questionDotToken || call.typeArguments || call.arguments.length !== 2 || !ts.isStringLiteral(call.arguments[0])) return null;
  const fn=call.arguments[1];
  if ((!ts.isArrowFunction(fn) && !ts.isFunctionExpression(fn)) || fn.asteriskToken || !ts.isBlock(fn.body)) return null;
  return {title:call.arguments[0].text, body:fn.body};
}
function plainTest(stmt) {
  if (!ts.isExpressionStatement(stmt) || !ts.isCallExpression(stmt.expression)) return null;
  const call=stmt.expression;
  if (!ts.isIdentifier(call.expression) || call.expression.text !== 'test' || call.questionDotToken || call.typeArguments || call.arguments.length !== 2 || !ts.isStringLiteral(call.arguments[0]) || !call.arguments[0].text) return null;
  const fn=call.arguments[1];
  if ((!ts.isArrowFunction(fn) && !ts.isFunctionExpression(fn)) || fn.asteriskToken || !ts.isBlock(fn.body)) return null;
  return call.arguments[0].text;
}
function groups(sf) {
  const out=new Map();
  function visit(statements, parents) {
    for (const stmt of statements) {
      const group=groupCall(stmt); if (!group) continue;
      const key=JSON.stringify([...parents,group.title]);
      if (out.has(key)) throw Error('ambiguous ordinary test group');
      out.set(key,group.body);
      visit(group.body.statements,[...parents,group.title]);
    }
  }
  visit(sf.statements,[]);
  return out;
}
function removeGroupedCases(name, baseline, target) {
  const b=parse(baseline,name), t=parse(target,name);
  const bg=groups(b), tg=groups(t), titles=new Set();
  // Existing titles anywhere in the file cannot be reused by an addition.
  function collect(node) {
    if (ts.isExpressionStatement(node)) { const title=plainTest(node); if (title !== null) titles.add(title); }
    ts.forEachChild(node,collect);
  }
  collect(b);
  const spans=[], addedTitles=[]; let cases=0;
  for (const [key,bb] of bg) {
    const tb=tg.get(key); if (!tb) throw Error('original ordinary test group missing or changed');
    const orig=[...bb.statements], current=[...tb.statements];
    const kept=[], runs=[]; let run=[];
    for (const stmt of current) {
      const title=plainTest(stmt);
      if (title !== null && !titles.has(title)) {
        titles.add(title); addedTitles.push(title); run.push(stmt); cases++;
        if (cases > 16) throw Error('too many added group tests');
      } else {
        if (run.length) { runs.push({index:kept.length,statements:run}); run=[]; }
        kept.push(stmt);
      }
    }
    if (run.length) runs.push({index:kept.length,statements:run});
    if (!runs.length) continue;
    if (orig.length !== kept.length) throw Error('original group statements changed');
    for (const {index,statements} of runs) {
      // Both sides are a group edge or an original plain test; at least one
      // original test must be adjacent. No insertion adjacent to a hook.
      if ((!index && index === orig.length) || (index && plainTest(orig[index-1]) === null) || (index < orig.length && plainTest(orig[index]) === null)) throw Error('unsupported group insertion boundary');
      const bl=index ? orig[index-1].end : bb.getStart(b)+1;
      const br=index < orig.length ? orig[index].getStart(b) : bb.end-1;
      const tl=index ? kept[index-1].end : tb.getStart(t)+1;
      const tr=index < kept.length ? kept[index].getStart(t) : tb.end-1;
      const gap=baseline.slice(bl,br), prefix=target.slice(tl,statements[0].getStart(t)), suffix=target.slice(statements.at(-1).end,tr);
      if (!/^\s*$/.test(gap) || !/^\s*$/.test(prefix) || !/^\s*$/.test(suffix)) throw Error('unsupported group insertion trivia');
      for (let i=1;i<statements.length;i++) if (!/^\s*$/.test(target.slice(statements[i-1].end,statements[i].getStart(t)))) throw Error('unsupported group insertion trivia');
      // Retain the complete original gap as an exact prefix or suffix. Only
      // whole added declarations and surrounding whitespace can be erased.
      if (prefix.startsWith(gap)) spans.push([tl+gap.length,tr]);
      else if (suffix.endsWith(gap)) spans.push([tl,tr-gap.length]);
      else throw Error('original group boundary trivia changed');
    }
  }
  for (const [start,end] of spans.sort((a,b)=>b[0]-a[0])) target=target.slice(0,start)+target.slice(end);
  return {target,cases,addedTitles};
}

export function preserveOriginalTest(name, baseline, target) {
  if (target === baseline) return {migration:false, assertions:0, cases:0, group_cases:0};
  const grouped=removeGroupedCases(name,baseline,target);
  target=grouped.target;
  if (name !== 'tests/api.test.ts') {
    if (target !== baseline) throw Error(`unsupported original test transformation: ${name}`);
    return {migration:false, assertions:0, cases:0, group_cases:grouped.cases};
  }
  const b = parse(baseline, name), t = parse(target, name);
  const bb = findSeed(b), tb = findSeed(t);
  const n = bb.statements.length;
  if (tb.statements.length < n) throw Error('seed statements removed');
  const additions = [...tb.statements].slice(n);
  if (additions.length > 16) throw Error('too many added assertions');
  let prev = tb.statements[n-1].end;
  for (const stmt of additions) {
    if (!/^\s*$/.test(target.slice(prev, stmt.getStart(t))) || !assertion.test(stmt.getText(t))) throw Error('unsupported added assertion');
    prev = stmt.end;
  }
  const top = [...t.statements].slice(b.statements.length);
  if (t.statements.length < b.statements.length || top.length > 16) throw Error('unsupported top-level statements');
  const titles = new Set();
  function collectTitles(node) { if (testCall(node)) titles.add(node.arguments[0].text); ts.forEachChild(node,collectTitles); }
  collectTitles(b);
  for (const title of grouped.addedTitles) titles.add(title);
  for (const stmt of top) {
    if (!ts.isExpressionStatement(stmt) || !newCase.test(stmt.getText(t)) || !testCall(stmt.expression)) throw Error('unsupported added test');
    const title = stmt.expression.arguments[0].text;
    if (titles.has(title) || title === seedTitle) throw Error('duplicate added test title');
    titles.add(title);
  }
  // Remove exactly the admitted added spans, preserving every byte of the original around them.
  const spans=[];
  if (additions.length) spans.push([tb.statements[n-1].end, additions.at(-1).end]);
  if (top.length) {
    const originalLast = t.statements[b.statements.length-1];
    let end = originalLast.end;
    for (const stmt of top) {
      if (!/^\s*$/.test(target.slice(end, stmt.getStart(t)))) throw Error('unsupported added test trivia');
      end = stmt.end;
    }
    spans.push([originalLast.end, top.at(-1).end]);
  }
  let reconstructed=target;
  for (const [start,end] of spans.sort((a,b)=>b[0]-a[0])) reconstructed=reconstructed.slice(0,start)+reconstructed.slice(end);
  const migrations = count(reconstructed, MIGRATED);
  if (migrations > 1 || count(baseline,OLD) !== 1) throw Error('migration anchor ambiguous');
  if (migrations === 1) reconstructed = reconstructed.replace(MIGRATED,OLD);
  if (reconstructed !== baseline) throw Error(`original test bytes changed outside finite rule: ${name}`);
  return {migration:migrations === 1, assertions:additions.length, cases:top.length, group_cases:grouped.cases};
}
