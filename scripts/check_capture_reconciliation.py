"""Synthetic audit controls; no model/API calls and no application assertions."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('capture',Path(__file__).with_name('verify_stream_capture.py'))
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class Controls(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def put(self,name,value):
  p=self.r/name;p.write_text(value if isinstance(value,str) else json.dumps(value));return p
 def stream(self,j,text,tokens,cost):
  usage={'prompt_tokens':tokens,'completion_tokens':1,'total_tokens':tokens+1,'cost':cost}
  body='data: '+json.dumps({'id':f'gen-{j}','choices':[{'index':0,'delta':{'content':text},'finish_reason':'stop'}],'usage':usage})+'\n\ndata: [DONE]\n\n'
  self.put(f'provider-response-{j}.sse',body);self.put(f'gateway-response-{j}.sse',body)
  return {'response_id':f'gen-{j}','usage':usage}
 def fixture(self):
  self.put('controller.json',{'exit_code':0,'requests':[{}]*4,'api_budget_exhausted':False});self.put('startup-verified.json',{})
  rows=[self.stream(1,'normal',10,.1),self.stream(3,'summary',20,.2),self.stream(4,'final',30,.3)]
  self.put('provider-usage.json',rows);self.put('provider-http-error-2.json','error code: 500\n')
  for j in range(1,5):
   content='ordinary'
   if j==3:content='You MUST summarize the conversation above into a structured summary now'
   if j==4:content='<conversation-checkpoint>summary</conversation-checkpoint>'
   self.put(f'native-request-{j}.json',{'messages':[{'role':'user','content':content}]});self.put(f'provider-request-{j}.json',{})
  steps=[{'tokens':{'input':n,'output':1,'cache':{'read':0,'write':0}},'cost':c,'reason':reason} for n,c,reason in [(10,.1,'tool-calls'),(30,.3,'stop')]]
  self.put('events.jsonl',''.join(json.dumps({'type':'step_finish','part':p})+'\n' for p in steps));return steps
 def cli(self):
  return subprocess.run([sys.executable,str(Path(audit.__file__)),str(self.r)],capture_output=True,text=True)
 def test_json_429(self):
  d=audit.failed_body(self.put('provider-http-error-2.json',{'error':{'code':429}}));self.assertEqual(d['provider_error_code'],429)
 def test_plain_500_not_http_status_attestation(self):
  d=audit.failed_body(self.put('provider-http-error-2.json','error code: 500\n'));self.assertEqual(d['provider_error_code'],500);self.assertFalse(d['http_status_independently_captured']);self.assertIn('unavailable',d['usage_status'])
 def test_unknown_html_is_not_recognized(self):
  d=audit.failed_body(self.put('provider-http-error-2.json','<html>upstream failed</html>'));self.assertIsNone(d['provider_error_code'])
 def test_explicit_504_stream_classified(self):
  self.put('provider-response-5.sse','data: '+json.dumps({'error':{'code':504}})+'\n');success,errors=audit.classify(self.r);self.assertFalse(success);self.assertEqual(errors[0]['provider_error_code'],504);self.assertTrue(errors[0]['gateway_stream_absent'])
 def test_noncontiguous_success_ids_and_compaction(self):
  self.fixture();p=self.cli();self.assertEqual(p.returncode,0,p.stderr);r=json.loads((self.r/'stream-integrity.json').read_text());self.assertEqual(r['requests'],4);self.assertEqual(r['calls'],3);self.assertEqual(r['verified_non_step_calls'],1);self.assertFalse(r['failed_call_billing_complete'])
 def test_refresh_compaction_form(self):
  self.fixture();self.put('native-request-3.json',{'messages':[{'role':'user','content':'Update the existing checkpoint in the conversation above into one consolidated summary.\nNewer history always takes precedence.'}]});p=self.cli();self.assertEqual(p.returncode,0,p.stderr)
 def test_success_content_corruption_rejected(self):
  self.fixture();p=self.r/'gateway-response-1.sse';p.write_text(p.read_text().replace('normal','lost'));self.assertNotEqual(self.cli().returncode,0)
 def test_unknown_failure_body_cannot_turn_green(self):
  self.fixture();self.put('provider-http-error-2.json','not a recognized error');p=self.cli();self.assertNotEqual(p.returncode,0);r=json.loads((self.r/'stream-integrity.json').read_text());self.assertFalse(r['checks']['recognized_failed_response_bodies'])
 def test_duplicate_usage_identity_rejected(self):
  self.fixture();p=self.r/'provider-usage.json';rows=json.loads(p.read_text());rows.append(rows[0]);p.write_text(json.dumps(rows));self.assertNotEqual(self.cli().returncode,0)
 def test_literal_done_is_not_terminal(self):
  usage=self.stream(1,'alpha[DONE]omega',10,.1);r=audit.parse(self.r/'provider-response-1.sse');self.assertEqual(r['semantic']['text']['0'],'alpha[DONE]omega');self.assertTrue(r['terminal_marker'])
 def test_changed_billable_cost_rejected(self):
  self.fixture();p=self.r/'provider-usage.json';rows=json.loads(p.read_text());rows[0]['usage']['cost']=9;p.write_text(json.dumps(rows));self.assertNotEqual(self.cli().returncode,0)
 def test_unconsumed_summary_rejected(self):
  self.fixture();self.put('native-request-4.json',{'messages':[{'role':'user','content':'summary not consumed'}]});self.assertNotEqual(self.cli().returncode,0)
 def test_dropped_native_step_rejected(self):
  self.fixture();p=self.r/'events.jsonl';p.write_text(p.read_text().splitlines()[0]+'\n');self.assertNotEqual(self.cli().returncode,0)
 def test_normalized_metadata_does_not_hide_counters(self):
  self.fixture();p=self.r/'provider-usage.json';rows=json.loads(p.read_text());rows[0]['usage']['prompt_tokens']=11;p.write_text(json.dumps(rows));self.assertNotEqual(self.cli().returncode,0)

if __name__=='__main__':unittest.main()
