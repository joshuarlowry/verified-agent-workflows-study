import { useEffect, useRef, useState, type FormEvent, type MutableRefObject } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Workspace = { id:string; name:string; role:'owner'|'member'; createdAt:string; openItemCount:number };
type WorkspaceDetail = { id:string; name:string; role:'owner'|'member'; createdAt:string; updatedAt:string };
type Item = { id:string; workspaceId:string; title:string; notes:string; status:'open'|'in_progress'|'done'; dueDate:string|null; version:number; createdBy:string; createdAt:string; updatedAt:string };
type Me = { user:{id:string;email:string;name:string}; workspaces:Workspace[] };
type Form = { id?:string; title:string; notes:string; status:Item['status']; dueDate:string };
class ApiError extends Error { constructor(message:string, public status:number, public fields:Record<string,string> = {}) { super(message); } }
async function api<T>(path:string, options:RequestInit = {}):Promise<T> {
  const response = await fetch(path,{ ...options, headers:{ ...(options.body ? {'Content-Type':'application/json'} : {}), ...options.headers } });
  if (!response.ok) { const data = await response.json().catch(() => ({})); throw new ApiError(data.error?.message || data.message || 'Request failed.',response.status,data.error?.fields || {}); }
  if (response.status === 204) return undefined as T;
  return response.json();
}
// SQLite BINARY compares UTF-8 bytes, unlike JavaScript's UTF-16 ordering.
function binary(a:string,b:string) { const x = new TextEncoder().encode(a), y = new TextEncoder().encode(b); for (let i=0;i<Math.min(x.length,y.length);i++) if (x[i] !== y[i]) return x[i]-y[i]; return x.length-y.length; }
const msg = (e:unknown) => e instanceof Error ? e.message : 'Request failed.';
const json = (method:string, body?:unknown):RequestInit => ({ method, ...(body === undefined ? {} : {body:JSON.stringify(body)}) });

function Auth({onLogin}:{onLogin:()=>Promise<void>}) {
  const [signup,setSignup] = useState(false), [error,setError] = useState(''), [pending,setPending] = useState(false);
  async function submit(e:FormEvent<HTMLFormElement>) {
    e.preventDefault(); const data = new FormData(e.currentTarget); setPending(true); setError('');
    try { await api(`/api/auth/${signup ? 'sign-up' : 'sign-in'}/email`,json('POST',{ email:data.get('email'),password:data.get('password'), ...(signup ? {name:data.get('name')} : {}) })); await onLogin(); }
    catch (err) { setError(msg(err)); } finally { setPending(false); }
  }
  return <section className="panel"><h2>{signup ? 'Create account' : 'Sign in'}</h2>{error && <p role="alert">{error}</p>}<form onSubmit={submit}>
    {signup && <label>Name<input name="name" autoComplete="name" required /></label>}
    <label>Email<input name="email" type="email" autoComplete="email" required /></label>
    <label>Password<input name="password" type="password" autoComplete={signup ? 'new-password':'current-password'} required /></label>
    <button disabled={pending}>{signup ? 'Create account':'Sign in'}</button>
  </form><button className="link" onClick={()=>{setSignup(!signup);setError('');}}>{signup ? 'Already have an account? Sign in':'Need an account? Create one'}</button></section>;
}
function WorkspaceCreator({first,onCreate,selectionGate}:{first:boolean;onCreate:(w:Workspace)=>void;selectionGate:MutableRefObject<number>}) {
  const [name,setName] = useState(''), [error,setError] = useState(''), [pending,setPending] = useState(false);
  const lifetime = useRef(0);
  useEffect(() => () => { lifetime.current++; }, []);
  async function submit(e:FormEvent) { e.preventDefault(); const selection = selectionGate.current, generation = lifetime.current; const alive = () => selectionGate.current === selection && lifetime.current === generation; setPending(true); setError(''); try { const w = await api<WorkspaceDetail>('/api/workspaces',json('POST',{name})); if (alive()) { setName(''); onCreate({ ...w, openItemCount: 0 }); } } catch(e) { if (alive()) setError(msg(e)); } finally { if (alive()) setPending(false); } }
  return <section className="panel"><h2>{first ? 'Create your first workspace':'Create a workspace'}</h2>{error && <p role="alert">{error}</p>}<form onSubmit={submit}><label>Workspace name<input value={name} onChange={e=>setName(e.target.value)} /></label><button disabled={pending}>Create workspace</button></form></section>;
}
function Board({ws,epoch,selectionGate,onMembershipRefresh}:{ws:Workspace;epoch:number;selectionGate:MutableRefObject<number>;onMembershipRefresh:()=>Promise<boolean>}) {
  const [items,setItems] = useState<Item[]|null>(null), [loadError,setLoadError] = useState(''), [loading,setLoading] = useState(true);
  const [form,setForm] = useState<Form|null>(null), [formError,setFormError] = useState(''), [fields,setFields] = useState<Record<string,string>>({}), [saving,setSaving] = useState(false);
  const [confirm,setConfirm] = useState<Item|null>(null), [deleting,setDeleting] = useState(false), [actionError,setActionError] = useState(''), [notice,setNotice] = useState('');
  const formGate = useRef(0), confirmGate = useRef(0), loadGate = useRef(0);
  const active = () => selectionGate.current === epoch;
  const actionLoad = useRef(false);
  function invalidateLoad() { if (actionLoad.current) { loadGate.current++; actionLoad.current = false; setLoading(false); } }
  function closeForm() { formGate.current++; invalidateLoad(); setForm(null); setSaving(false); setFormError(''); setFields({}); }
  function openForm(value:Form) { formGate.current++; invalidateLoad(); setForm(value); setSaving(false); setFormError(''); setFields({}); setNotice(''); }
  function closeConfirm() { confirmGate.current++; invalidateLoad(); setConfirm(null); setDeleting(false); setActionError(''); }
  async function load(valid?:()=>boolean) {
    const generation = ++loadGate.current; actionLoad.current = !!valid; setLoading(true); setLoadError('');
    const alive = () => active() && generation === loadGate.current && (!valid || valid());
    try { const data = await api<{workspaceId:string;items:Item[]}>(`/api/workspaces/${encodeURIComponent(ws.id)}/items`); if (alive()) setItems(data.items); }
    catch(e) { if (alive()) { setLoadError(msg(e)); if (e instanceof ApiError && e.status === 404) setItems(null); } }
    finally { if (active() && generation === loadGate.current) { actionLoad.current = false; setLoading(false); } }
  }
  useEffect(()=>{ void load(); return () => { loadGate.current++; formGate.current++; confirmGate.current++; }; }, []); // keyed selection lifetime
  async function retry() { try { const still = await onMembershipRefresh(); if (active() && still) await load(); } catch(e) { if (active()) setLoadError(msg(e)); } }
  async function save(e:FormEvent) {
    e.preventDefault(); if (!form || saving) return;
    const generation = formGate.current, snapshot = form; setSaving(true); setFormError(''); setFields({});
    const alive = () => active() && formGate.current === generation;
    try {
      await api(snapshot.id ? `/api/items/${encodeURIComponent(snapshot.id)}` : `/api/workspaces/${encodeURIComponent(ws.id)}/items`, json(snapshot.id ? 'PATCH':'POST',{ title:snapshot.title,notes:snapshot.notes,status:snapshot.status,dueDate:snapshot.dueDate || null }));
      if (!alive()) return;
      closeForm(); const next = formGate.current; setNotice(snapshot.id ? 'Work item updated.':'Work item created.'); await load(() => formGate.current === next);
    } catch(e) { if (alive()) { setFormError(msg(e)); if (e instanceof ApiError) setFields(e.fields); } }
    finally { if (alive()) setSaving(false); }
  }
  async function remove() {
    if (!confirm || deleting) return; const generation = confirmGate.current, snapshot = confirm; setDeleting(true); setActionError('');
    const alive = () => active() && confirmGate.current === generation;
    try { await api(`/api/items/${encodeURIComponent(snapshot.id)}`,json('DELETE')); if (!alive()) return; closeConfirm(); const next = confirmGate.current; setNotice('Work item deleted.'); await load(() => confirmGate.current === next); }
    catch(e) { if (alive()) setActionError(msg(e)); } finally { if (alive()) setDeleting(false); }
  }
  function field(name:string) { return { 'aria-invalid': !!fields[name], 'aria-describedby': fields[name] ? `error-${name}` : undefined }; }
  return <section><p>Your role: {ws.role === 'owner' ? 'Owner':'Member'}</p>
    <button aria-expanded={!!form && !form.id} onClick={()=> form && !form.id ? closeForm() : openForm({title:'',notes:'',status:'open',dueDate:''})}>New work item</button>
    {form && <form className="panel" onSubmit={save} noValidate><h2>{form.id ? 'Edit work item':'New work item'}</h2>{formError && <p role="alert">{formError}</p>}
      <label>Title<input value={form.title} onChange={e=>setForm({...form,title:e.target.value})} {...field('title')} /></label>{fields.title && <p id="error-title">{fields.title}</p>}
      <label>Status<select value={form.status} onChange={e=>setForm({...form,status:e.target.value as Item['status']})} {...field('status')}><option value="open">Open</option><option value="in_progress">In progress</option><option value="done">Done</option></select></label>{fields.status && <p id="error-status">{fields.status}</p>}
      <label>Due date<input type="date" value={form.dueDate} onChange={e=>setForm({...form,dueDate:e.target.value})} {...field('dueDate')} /></label>{fields.dueDate && <p id="error-dueDate">{fields.dueDate}</p>}
      <label>Notes<textarea value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})} {...field('notes')} /></label>{fields.notes && <p id="error-notes">{fields.notes}</p>}
      <button disabled={saving}>{form.id ? 'Save changes':'Create work item'}</button> <button type="button" onClick={closeForm}>Cancel</button>
    </form>}
    <p role="status">{notice}</p>
    {loading && <p>Loading work items…</p>}
    {loadError && <div role="alert"><p>Could not load work items: {loadError}</p><button onClick={()=>void retry()}>Retry</button></div>}
    {actionError && <p role="alert">{actionError}</p>}
    {items && <section aria-label="Work items"><h2>Work items</h2>{items.length === 0 && <p>No work items in this workspace yet. Use "New work item" to add the first one.</p>}
      {items.map(it=><article key={it.id} className="item"><h3>{it.title}</h3><p>{({open:'Open',in_progress:'In progress',done:'Done'})[it.status]}</p><p>Updated {it.updatedAt.slice(0,10)} · {it.dueDate ? `Due ${it.dueDate}`:'No due date'}</p><p className="notes">{it.notes}</p>
        <button onClick={()=>openForm({id:it.id,title:it.title,notes:it.notes,status:it.status,dueDate:it.dueDate || ''})}>Edit {it.title}</button>{' '}
        {confirm?.id === it.id ? <><button disabled={deleting} onClick={()=>void remove()}>Confirm delete {it.title}</button> <button onClick={closeConfirm}>Cancel</button></> : <button onClick={()=>{confirmGate.current++;invalidateLoad();setConfirm(it);setDeleting(false);setActionError('');}}>Delete {it.title}</button>}
      </article>)}
    </section>}
  </section>;
}
function App() {
  const [me,setMe] = useState<Me|null>(null), [checking,setChecking] = useState(true), [error,setError] = useState(''), [selected,setSelected] = useState(''), [epoch,setEpoch] = useState(0), [notice,setNotice] = useState('');
  const selectionGate = useRef(0), selectedRef = useRef('');
  function select(id:string) { if (id === selectedRef.current) return; selectedRef.current = id; selectionGate.current++; setEpoch(selectionGate.current); setSelected(id); setNotice(''); }
  async function refresh() { const before = selectedRef.current, generation = selectionGate.current; const data = await api<Me>('/api/me'); if (generation !== selectionGate.current) return false; setMe(data); const exists = data.workspaces.some(w=>w.id === before); if (!exists) select(data.workspaces[0]?.id || ''); return exists; }
  useEffect(()=>{ refresh().catch(e=>{ if (!(e instanceof ApiError && e.status === 401)) setError(msg(e)); }).finally(()=>setChecking(false)); }, []);
  async function signOut() { try { await api('/api/auth/sign-out',json('POST',{})); if (!selectedRef.current) { selectionGate.current++; setEpoch(selectionGate.current); } else select(''); setMe(null); setError(''); } catch(e) { setError(msg(e)); } }
  const ws = me?.workspaces.find(w=>w.id === selected);
  return <main><header><h1>Workboard Lab</h1>{me && <div>{me.user.email} <button onClick={()=>void signOut()}>Sign out</button></div>}</header>
    {error && <p role="alert">{error}</p>}
    {checking ? <p>Checking session…</p> : !me ? <Auth onLogin={async()=>{await refresh();}} /> : <>
      {me.workspaces.length > 0 && <label>Workspace<select value={selected} onChange={e=>select(e.target.value)}>{me.workspaces.map(w=><option value={w.id} key={w.id}>{w.name} ({w.openItemCount ?? 0})</option>)}</select></label>}
      {ws && <Board key={`board-${epoch}`} ws={ws} epoch={epoch} selectionGate={selectionGate} onMembershipRefresh={refresh} />}
      <p role="status">{notice}</p><WorkspaceCreator key={`creator-${epoch}`} selectionGate={selectionGate} first={!me.workspaces.length} onCreate={w=>{setMe({...me,workspaces:[...me.workspaces,w].sort((a,b)=>binary(a.name,b.name) || binary(a.createdAt,b.createdAt) || binary(a.id,b.id))}); select(w.id); setNotice('Workspace created.');}} />
    </>}
  </main>;
}
createRoot(document.getElementById('root')!).render(<App />);