"""Derive reviewable patches from frozen source; preserve author artifacts."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

REPO=Path(__file__).resolve().parents[1]
ROOT=Path('/home/josh/.local/state/study2-setup/clean-20261107T122746Z')


def hashes(source):
    names=subprocess.check_output(['git','-C',str(source),'ls-files','-z']).decode().split('\0')
    result={}
    for name in names:
        if not name:continue
        path=source/name
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):raise ValueError('Invalid source path')
        result[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def copy_files(source,inventory,target):
    for name,sha in inventory.items():
        path=source/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('Changed frozen source')
        dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dst)


def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True)


def main():
    if os.geteuid()!=0:raise SystemExit('Authorized preparation controller required')
    started=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    job=ROOT/('controller-fixture-patch-export-'+stamp);job.mkdir();shutil.copy2(__file__,job/'controller-source.py')
    baseline=ROOT/'baseline-construction-20261107T183146Z/workspace/output/baseline'
    base=hashes(baseline);rows=[]
    fixtures=[('reference',ROOT/'c1-reference-checks-20261107T201734Z/workspace/output/c1-packet/reference','4d610cb01c838f924566fd43159939d495965197'),('alternative',ROOT/'c1-alternate-20261107T211533Z/workspace/output/c1-alternate/source','eb7d00f932f15522d3647197455b9c80eb1b6f3b')]
    for label,source,expected in fixtures:
        head=git(source,'rev-parse','HEAD').stdout.decode().strip()
        if head!=expected or git(source,'status','--porcelain').stdout.strip():raise ValueError('Fixture endpoint changed')
        frozen=hashes(source)
        with tempfile.TemporaryDirectory(prefix='study2-patch-export-') as folder:
            work=Path(folder);copy_files(baseline,base,work);git(work,'init','-q')
            git(work,'config','user.name','Study controller (mechanical export)');git(work,'config','user.email','controller@study.invalid')
            git(work,'add','--all');git(work,'commit','-q','-m','Exact frozen baseline source; mechanical export only')
            for removed in set(base)-set(frozen):(work/removed).unlink()
            copy_files(source,frozen,work);git(work,'add','-N','--all')
            patch=git(work,'diff','--binary','HEAD','--').stdout
            target=job/(label+'.application-only.patch');target.write_bytes(patch)
            git(work,'reset','--hard','-q','HEAD');git(work,'clean','-fdq')
            git(work,'apply','--check',str(target));git(work,'apply',str(target));git(work,'add','--all')
            if hashes(work)!=frozen:raise ValueError('Patch does not reproduce exact frozen source')
        if hashes(source)!=frozen:raise ValueError('Original fixture changed during export')
        rows.append({'label':label,'original_source_commit':head,'source_files':len(frozen),'patch':target.name,
                     'patch_sha256':hashlib.sha256(patch).hexdigest(),'patch_bytes':len(patch),
                     'roundtrip_exact_source_match':True,'original_source_unchanged':True,
                     'source_inventory_sha256':hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()})
    report={'kind':'controller_derived_patch_packaging_extension_not_feature_repair',
            'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'elapsed_seconds':time.monotonic()-started,'external_model_calls':0,
            'interactive_coordinator_usage':'unavailable, not zero', 'baseline_commit':git(baseline,'rev-parse','HEAD').stdout.decode().strip(),
            'artifacts':rows,'original_author_patches_replaced':False,
            'scope':'Same deterministic export applied to both frozen fixtures. Exact application bytes including alternative lock metadata retained; original author patch/source preserved. Patches remain private. Not source approval, test acceptance or an application edit.'}
    (job/'controller.json').write_text(json.dumps(report,indent=2)+'\n')
    public=REPO/'setup/c1-controller-patch-export.json';public.write_text(json.dumps(report,indent=2)+'\n');os.chown(public,1000,1000)
    print(json.dumps({'job':str(job),'roundtrips_passed':len(rows),'original_source_unchanged':True}))


if __name__=='__main__':main()
