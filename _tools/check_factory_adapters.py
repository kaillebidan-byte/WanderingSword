#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factory actionが恒久adapter・固定workflowへ接続されていることを検査する。"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent; P4=ROOT/'_phase4_proofread'
FLOW=P4/'FACTORY_FLOW_CONTRACT.json'; REQUEST=P4/'FACTORY_REQUEST_CONTRACT.json'
RESOURCES={
 'initializer':'_tools/fixed_cycle_initializer.py','request_executor':'_tools/factory_request_executor.py','request_workflow':'.github/workflows/translation-factory-execute.yml',
 'encoding':'_tools/fixed_encoding_pipeline.py','encoding_executor':'_tools/factory_encoding_executor.py','encoding_workflow':'.github/workflows/translation-factory-encode.yml',
 'finalizer':'_tools/fixed_release_finalizer.py','finalization_workflow':'.github/workflows/translation-factory-finalize.yml'}
def load(p:Path)->dict[str,Any]:
 v=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(v,dict): raise ValueError(f'top level must be object: {p.relative_to(ROOT)}')
 return v
def validate(flow:dict[str,Any],request:dict[str,Any],texts:dict[str,str])->list[str]:
 e=[]
 expected_top={'request_contract':'_phase4_proofread/FACTORY_REQUEST_CONTRACT.json','execution_workflow':RESOURCES['request_workflow'],'encoding_workflow':RESOURCES['encoding_workflow'],'finalization_workflow':RESOURCES['finalization_workflow']}
 for k,v in expected_top.items():
  if flow.get(k)!=v:e.append(f'factory flow {k} mismatch')
 actions=flow.get('actions',{})
 expected_actions={
  'initialize_next_cycle_from_reservation':{'executor':'fixed_cycle_initializer','adapter':RESOURCES['initializer']},
  'encode_recorded_decisions':{'executor':'fixed_encoding_pipeline','adapter':RESOURCES['encoding'],'execution_workflow':RESOURCES['encoding_workflow']},
  'finalize_release_state':{'executor':'fixed_release_finalizer','adapter':RESOURCES['finalizer'],'request_pattern':'_factory_requests/finalize-release-*.json','execution_workflow':RESOURCES['finalization_workflow'],'resulting_transport':'awaiting_private_merge'},
 }
 for name,expected in expected_actions.items():
  item=actions.get(name)
  if not isinstance(item,dict): e.append(f'action {name} missing'); continue
  for k,v in expected.items():
   if item.get(k)!=v:e.append(f'action {name}.{k} mismatch')
 if request.get('contract_id')!='translation-factory-request-v1' or request.get('executor')!=RESOURCES['request_executor']:e.append('factory request contract mismatch')
 markers={
  'request':['name: Translation factory executor','factory_request_executor.py','fixed_cycle_initializer.py','git rm'],
  'encoding':['name: Translation factory encoding','factory_encoding_executor.py','fixed_encoding_pipeline.py','ready_for_public_ci'],
  'finalization':['name: Translation factory finalization','fixed_release_finalizer.py','finalization-inputs.json','check_release_evidence.py','awaiting_private_merge','git rm'],
 }
 for key,items in markers.items():
  for marker in items:
   if marker not in texts[key]: e.append(f'{key} workflow lacks marker: {marker}')
 combined=texts['encoding']+'\n'+texts['encoding_code']
 for marker in ('apply_owner_assignment_v2','check_batch_planning.py'):
  if marker not in combined:e.append(f'encoding path lacks marker: {marker}')
 for text in (texts['request'],texts['encoding'],texts['finalization']):
  for forbidden in ('oneoff','web.run','workflow_dispatch:'):
   if forbidden in text:e.append(f'workflow contains forbidden fallback: {forbidden}')
 return e
def main()->int:
 try:
  flow=load(FLOW); request=load(REQUEST)
  for p in RESOURCES.values():
   if not (ROOT/p).is_file():raise ValueError(f'missing factory resource: {p}')
  texts={'request':(ROOT/RESOURCES['request_workflow']).read_text(encoding='utf-8'),'encoding':(ROOT/RESOURCES['encoding_workflow']).read_text(encoding='utf-8'),'finalization':(ROOT/RESOURCES['finalization_workflow']).read_text(encoding='utf-8'),'encoding_code':(ROOT/RESOURCES['encoding']).read_text(encoding='utf-8')}
 except (OSError,ValueError,json.JSONDecodeError) as exc: print(f'ERROR: {exc}'); return 1
 errors=validate(flow,request,texts); print('=== Translation factory adapters ===')
 for x in errors:print(f'ERROR: {x}')
 if errors:print(f'FAILED: {len(errors)} error(s)'); return 1
 print('OK: initializer, encoding, and release finalization use permanent fixed adapters'); return 0
if __name__=='__main__':raise SystemExit(main())
