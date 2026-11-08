"""Passive public status: metadata only, no subject text, checks or feedback."""
from pathlib import Path
import datetime,fcntl,json,os,sqlite3,subprocess,sys,time
from zoneinfo import ZoneInfo
REPO=Path(__file__).resolve().parents[1]
BLOCK=Path('/home/josh/.local/state/study2-setup/clean-20261107T122746Z/c1-block-staging-20261108T0550')
FILES=['setup/launch.json','setup/status.json','setup/RUN_STATUS.md']
def east(value):return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).strftime('%b %d, %Y at %I:%M:%S %p %Z')
def main():
 if os.geteuid()!=0:raise SystemExit('Root passive observer required')
 previous=None
 while True:
  if not (BLOCK/'collection.json').exists():time.sleep(5);continue
  state=json.loads((BLOCK/'collection.json').read_text());dispatched={};event=None
  ledger=BLOCK/'study-ledger.sqlite'
  if ledger.exists():
   db=sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
   try:
    for ident,body,status in db.execute('SELECT id,body,state FROM runs'):dispatched[ident]=status
    events=[json.loads(x[0]) for x in db.execute('SELECT body FROM events ORDER BY seq')]
    if events:event=events[-1]['utc']
   finally:db.close()
  rows=[{k:v for k,v in row.items() if k in ['position','arm','repetition','run_id','status','endpoint_reason','native_exit_code','actual_provider_resolution','backup_error_type']} for row in state['runs']]
  signature=json.dumps({'status':state['status'],'rows':rows,'dispatched':dispatched},sort_keys=True)
  if signature!=previous:
   now=datetime.datetime.now(datetime.timezone.utc).isoformat();ended=sum(x not in ['active','running'] for x in dispatched.values())
   data={'kind':'registered_C1_calibration_metadata','status':state['status'],'snapshot_at_utc':now,'snapshot_at_eastern':east(now),'event_at_utc':event or state['started']['utc'],'event_at_eastern':east(event or state['started']['utc']),'cohort_id':BLOCK.parent.name,'calibration_block_size':10,'calibration_dispatched':len(dispatched),'calibration_endpoints':ended,'scored_runs':0,'rows':rows,'quality':'Not graded; an endpoint is not verified completion.','scope':'First10of40registered calibration attempts;165scored slots remain. Passive status observer makes no model calls or quality interventions.'}
   lines=['# Current run status','','**Status published:** '+data['snapshot_at_eastern'],'','**Latest ledger event:** '+data['event_at_eastern'],'',f"C1 calibration: **{len(dispatched)}/10 dispatched; {ended}/10 endpoints recorded.** Scored: **0**.",'','| Workflow | Repetition | State | Endpoint |','|---|---|---|---|']
   lines += [f"| {x['arm']} | {x['repetition']} | {dispatched.get(x['run_id'],x['status'])} | {x.get('endpoint_reason','—')} |" for x in rows]
   lines += ['','Endpoints remain ungraded. A final return or deadline may leave incomplete work. Backups run between workflows. All displayed times use America/New_York. [Frozen admission](c1-calibration-admission.json).','']
   with (REPO/'.git/study-status.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    for name,body in [(FILES[0],json.dumps(data,indent=2)+'\n'),(FILES[1],json.dumps(data,indent=2)+'\n'),(FILES[2],'\n'.join(lines))]:
     p=REPO/name;p.write_text(body);os.chown(p,1000,1000)
    def git(*args):return subprocess.run(['runuser','-u','josh','--','git','-C',str(REPO),*args],capture_output=True,text=True,check=True)
    if git('diff','--cached','--name-only').stdout.strip():raise RuntimeError('Unrelated staged files; stop passive publisher')
    git('add','--',*FILES)
    if git('diff','--cached','--name-only').stdout.strip():git('commit','-m','Update registered calibration status in Eastern time')
    git('push','origin','HEAD')
   previous=signature
  if state['status']!='running':return
  time.sleep(5)
if __name__=='__main__':main()
