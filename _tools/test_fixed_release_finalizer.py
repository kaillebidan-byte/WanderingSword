#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('fixed_release_finalizer',ROOT/'fixed_release_finalizer.py')
M=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=M; SPEC.loader.exec_module(M)
def w(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
  with tempfile.TemporaryDirectory() as td:
    root=Path(td); p4=root/'_phase4_proofread'; p4.mkdir()
    train='yuwen-mowen-train-27'; branch='agent/yuwen-mowen-train-27'; pr=166; ci='1'*40; asset='2'*40
    current={'schema_version':8,'updated_at':'2026-07-28','translation_base_commit':'3'*40,'state_base_commit':'4'*40,'current_cluster':'wudang_core','current_pair':'宇文逸↔莫問','stage':'translation_reaudit_in_progress','status':'verified','last_completed_batch':157,'last_reviewed_batch':157,'pair_applied_keys':1351,'project_applied_keys':1727,'build_status':'verified_not_deployed','game_verified':'not_started','last_merged_translation_pr':162,'checkpoint':{},'operation_mode':{},'pr_continuity':{},'session_bootstrap':{},'mandatory_read_order':[],'ci_train':{'train_id':train,'branch':branch,'draft_pr':pr,'status':'ready_for_public_ci','transport_status':'ready_for_public_ci','private_stage':{'stage':'translation_frozen','status':'complete','transport_status':'ready_for_public_ci'},'totals':{}},'release_evidence':'old'}
    state={'train_id':train,'stage':'translation_frozen','cycle_control':{},'wave':{'packets':[{'review_record':{'apply_status':'pending'}}]},'transport':{'status':'ready_for_public_ci','pr':pr,'history':[{'status':'ready_for_public_ci'}]}}
    manifest={'schema_version':2,'phase':'phase1_wave','train_id':train,'branch':branch,'draft_pr':pr,'status':'ready_for_public_ci','transport':{'status':'ready_for_public_ci','pr':pr},'bundles':[{'batch':158,'apply_status':'pending','scene_groups':['x'],'keep_keys':59}],'totals':{'reviewed_rows':62,'fix_keys':3},'private_stage':{'status':'complete','transport_status':'ready_for_public_ci'},'next_release':{}}
    audit={'project':{'latest_build':{'applied_keys':1727,'record_index':['_phase4_proofread/APPLIED_FIXES_YUWEN_MOWEN_BATCH158_2026-07-29.md']}},'pair_status':{'宇文逸↔莫問':{'applied_keys':1351}}}
    for n,v in [('CURRENT_WORK.json',current),('PRIVATE_STAGE_STATE.json',state),('CI_TRAIN_MANIFEST.json',manifest),('audit_status.json',audit)]: w(p4/n,v)
    (p4/'APPLIED_FIXES_YUWEN_MOWEN_BATCH158_2026-07-29.md').write_text('ok\n',encoding='utf-8')
    req={'schema_version':1,'contract_id':'release-finalization-request-v1','operation':'finalize_release_state','executor':'fixed_release_finalizer','branch':branch,'pr':pr,'orchestrator_run_id':10,'ci_head':ci,'asset_head':asset,'apply_changed':True,'date':'2026-07-29','next_scene':'5331_2','next_source':{'artifact_workflow':'Release train orchestrator','artifact_name':'relation-audit-evidence','artifact_file':'yuwen_mowen.json','artifact_run':10,'artifact_id':11,'artifact_digest':'sha256:x','artifact_head':ci,'freshness_rule':'after merge refresh'},'notes':['ok']}
    art={'schema_version':1,'pr':pr,'orchestrator_run_id':10,'ci_head':ci,'asset_head':asset,'apply_changed':True}
    result=M.finalize(req,art,branch=branch,p4=p4)
    assert result['batch']==158 and result['next_scene']=='5331_2'
    c=json.loads((p4/'CURRENT_WORK.json').read_text(encoding='utf-8')); assert c['checkpoint']['status']=='verified' and c['ci_train']['transport_status']=='awaiting_private_merge'
    s=json.loads((p4/'PRIVATE_STAGE_STATE.json').read_text(encoding='utf-8')); assert s['transport']['status']=='awaiting_private_merge'
    packet=json.loads((p4/'NEXT_TASK_PACKET.json').read_text(encoding='utf-8')); assert packet['reservation']['status']=='reserved_only' and packet['scene_groups']==['5331_2']
    print('test_fixed_release_finalizer: OK')
if __name__=='__main__': main()
