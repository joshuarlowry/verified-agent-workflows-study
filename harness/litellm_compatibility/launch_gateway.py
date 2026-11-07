"""Mandatory clean-cohort entry point; refuse a silently unpatched gateway."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

def refuse(reason):
    os.write(2,(json.dumps({'event':'study_gateway_refused','reason':reason})+'\n').encode())
    raise SystemExit(78)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--patch-sha256',required=True)
    parser.add_argument('--verify-only',action='store_true')
    args,rest=parser.parse_known_args()
    if os.environ.get('STUDY_LITELLM_DONE_FIX') != '1':
        refuse('Overlay activation must be exactly 1')
    patch=Path(__file__).with_name('sitecustomize.py').resolve()
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=args.patch_sha256:
        refuse('Overlay differs from frozen hash')
    sitecustomize=sys.modules.get("sitecustomize")
    if sitecustomize is None:
        refuse("Overlay was not imported at Python startup")
    if Path(sitecustomize.__file__).resolve()!=patch:
        refuse('Unexpected Python startup module')
    import litellm.llms.base_llm.base_model_iterator as module
    if getattr(module,'_study_done_fix_applied',False) is not True:
        refuse('Iterator repair is not active')
    os.write(2,(json.dumps({'event':'study_gateway_verified','patch_sha256':args.patch_sha256,'upstream_source_sha256':sitecustomize.EXPECTED_SOURCE_SHA256})+'\n').encode())
    if args.verify_only:return
    if rest and rest[0]=='--':rest=rest[1:]
    if '--config' not in rest:refuse('Explicit private gateway configuration required')
    cli=Path(sys.prefix)/'bin/litellm'
    if not cli.is_file():refuse('Pinned environment CLI missing')
    sys.argv=[str(cli),*rest]
    runpy.run_path(str(cli),run_name='__main__')

if __name__=='__main__':main()
