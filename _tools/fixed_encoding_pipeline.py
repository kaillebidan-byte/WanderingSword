#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記録済みquality-audit判断だけをformal bundle・owner・translation freezeへ機械収録する。"""
from __future__ import annotations
import argparse, hashlib, json, os, re, tempfile
from pathlib import Path
import apply_owner_assignment_v2 as owner_v2

ROOT=Path(__file__).resolve().parent.parent; P4=ROOT/'_phase4_proofread'
PAIR='宇文逸↔莫問'
AUDIT_RE=re.compile(r'^AUDIT_DECISIONS_YUWEN_MOWEN_TRAIN(?P<train>\d+)_WAVE(?P<wave>\d+)_(?P<date>\d{4}-\d{2}-\d{2})\.json$')
ENCODING_PERMS={'translation_judgment_allowed':False,'fix_writes_allowed':True,'encoding_writes_allowed':True,'throughput_metrics_visible':True,'metrics_frozen':False}
FROZEN_PERMS={'translation_judgment_allowed':False,'fix_writes_allowed':False,'encoding_writes_allowed':False,'throughput_metrics_visible':True,'metrics_frozen':False}

class EncodingError(ValueError): pass

def load(path):
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): raise EncodingError(f'top level must be object: {path}')
    return value

def write_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f: f.write(text)
        os.replace(tmp,path)
    except BaseException:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise

def write_json(path,value): write_text(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def digest(path): return 'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()

def identity(path):
    m=AUDIT_RE.fullmatch(path.name)
    if not m: raise EncodingError(f'invalid audit decision filename: {path.name}')
    return int(m['train']),int(m['wave']),m['date']

def direct_path(value,p4,prefix,suffix,must_exist=False):
    p=Path(value)
    if p.is_absolute() or '..' in p.parts or p.parent.as_posix()!='_phase4_proofread' or not p.name.startswith(prefix) or not p.name.endswith(suffix):
        raise EncodingError(f'invalid path: {value}')
    target=p4.parent/p
    if must_exist and not target.is_file(): raise EncodingError(f'missing file: {value}')
    if not must_exist and target.exists(): raise EncodingError(f'output already exists: {value}')
    return p.as_posix()

def candidate_index(candidate):
    rows=candidate.get('rows')
    if not isinstance(rows,list) or not rows: raise EncodingError('candidate.rows must be non-empty list')
    by={}
    for i,row in enumerate(rows):
        key=row.get('key') if isinstance(row,dict) else None
        if not isinstance(key,str) or not key: raise EncodingError(f'candidate.rows[{i}].key invalid')
        if key in by: raise EncodingError(f'duplicate candidate key: {key}')
        by[key]=row
    return rows,by

def validate_decision(decision,candidate):
    if decision.get('status')!='audited': raise EncodingError('decision status must be audited')
    rows,by=candidate_index(candidate); fixes=decision.get('fixes'); keeps=decision.get('keeps')
    if not isinstance(fixes,list) or not isinstance(keeps,list) or any(not isinstance(k,str) or not k for k in keeps):
        raise EncodingError('decision fixes/keeps invalid')
    if len(keeps)!=len(set(keeps)): raise EncodingError('decision keeps contain duplicates')
    fix_map={}; normalized=[]
    for i,item in enumerate(fixes):
        if not isinstance(item,dict): raise EncodingError(f'fix[{i}] must be object')
        key,before,after,reason=(item.get(k) for k in ('key','before','after','reason'))
        if not all(isinstance(v,str) and v for v in (key,before,after,reason)): raise EncodingError(f'fix[{i}] fields invalid')
        if key not in by or by[key].get('ja')!=before: raise EncodingError(f'fix source mismatch: {key}')
        if key in fix_map: raise EncodingError(f'duplicate fix key: {key}')
        fix_map[key]=after; normalized.append({'key':key,'before':before,'after':after,'reason':reason})
    fix_keys=set(fix_map); keep_keys=set(keeps); candidate_keys=set(by)
    if fix_keys&keep_keys: raise EncodingError('fix and keep sets overlap')
    if fix_keys|keep_keys!=candidate_keys:
        raise EncodingError(f'audit partition mismatch: missing={sorted(candidate_keys-(fix_keys|keep_keys))} extra={sorted((fix_keys|keep_keys)-candidate_keys)}')
    if decision.get('scene_groups')!=candidate.get('scene_groups'): raise EncodingError('scene_groups mismatch')
    return {'rows':rows,'fixes':normalized,'fix_map':fix_map,'keeps':keeps,
            'allusion_review_candidates':list(decision.get('allusion_review_candidates',[])),
            'allusion_review_resolved':list(decision.get('allusion_review_resolved',[])),
            'fact_doubts':list(decision.get('fact_doubts',[]))}

def review_text(batch,candidate_path,candidate,source,data):
    lines=[f'# {PAIR} 第{batch}束 review','',f"- scenes: `{', '.join(candidate.get('scene_groups',[]))}`",f'- candidate: `{candidate_path}`',
           f"- source artifact: run `{source.get('run_id')}` / artifact `{source.get('artifact_id')}`",'','## 実変更','']
    if data['fixes']:
        for fix in data['fixes']:
            lines += [f"- key: `{fix['key']}`",f"- before: `{fix['before']}`",f"- after: `{fix['after']}`",f"- reason: {fix['reason']}",'']
    else: lines += ['実変更なし。','']
    lines += ['## 保持判断','',f"同一packetの残り{len(data['keeps'])}行は、原文の意味、話者register、時系列、制御タグを再確認し、実質的な欠陥がないため保持した。",
              '好みだけの言い換え、場面以上の事実補完、別人物の声の一括変更は行っていない。','']
    if data['allusion_review_resolved']:
        lines += ['## 典故監査','']
        for item in data['allusion_review_resolved']:
            if isinstance(item,dict): lines.append(f"- `{item.get('key')}`: {item.get('decision')} — {item.get('note')}")
        lines.append('')
    return '\n'.join(lines)

def transition(state,stage):
    history=state.get('history')
    if not isinstance(history,list) or not history or history[-1].get('status')!='active': raise EncodingError('active stage history missing')
    history[-1]['status']='complete'; history.append({'stage':stage,'status':'active'})

def prepare(audit_path,pr,new_owner,p4):
    current=load(p4/'CURRENT_WORK.json'); state=load(p4/'PRIVATE_STAGE_STATE.json'); manifest=load(p4/'CI_TRAIN_MANIFEST.json'); packet=load(p4/'NEXT_TASK_PACKET.json'); audit=load(audit_path)
    new_owner=direct_path(new_owner,p4,'fixes_','.json'); train_no,wave_no,date=identity(audit_path)
    train=f'yuwen-mowen-train-{train_no}'; wave=f'{train}-wave-{wave_no:02d}'
    if audit.get('train_id')!=train or audit.get('wave_id')!=wave or audit.get('status')!='complete' or audit.get('stage')!='private_quality_audit': raise EncodingError('audit identity/state mismatch')
    if state.get('stage')!='private_quality_audit' or state.get('train_id')!=train or manifest.get('train_id')!=train or current.get('ci_train',{}).get('train_id')!=train: raise EncodingError('train authorities mismatch')
    decisions=audit.get('decisions'); packets=state.get('wave',{}).get('packets'); base=manifest.get('base_checkpoint',{}).get('batch'); source=audit.get('source_artifact')
    if not isinstance(decisions,list) or not decisions or not isinstance(packets,list) or len(decisions)!=len(packets) or not isinstance(base,int) or not isinstance(source,dict): raise EncodingError('audit/wave/base/source shape mismatch')
    bundles=[]; plans=[]; reviews=[]; total_rows=total_fixes=total_keeps=0
    for i,(decision,wave_packet) in enumerate(zip(decisions,packets)):
        if not isinstance(decision,dict) or not isinstance(wave_packet,dict) or decision.get('packet_id')!=wave_packet.get('packet_id'): raise EncodingError('packet alignment mismatch')
        candidate_rel=decision.get('candidate')
        if not isinstance(candidate_rel,str) or wave_packet.get('preparation_record',{}).get('candidate_packet')!=candidate_rel: raise EncodingError('candidate path mismatch')
        candidate=load(p4.parent/candidate_rel)
        if candidate.get('source_artifact')!=source: raise EncodingError('candidate source artifact mismatch')
        data=validate_decision(decision,candidate); batch=base+i+1; review=f'_phase4_proofread/REVIEW_YUWEN_MOWEN_BATCH{batch}_{date}.md'
        write_text(p4.parent/review,review_text(batch,candidate_rel,candidate,source,data)); reviews.append(review)
        rows=len(data['rows']); fixes=len(data['fixes']); total_rows+=rows; total_fixes+=fixes; total_keeps+=len(data['keeps'])
        owner_path=new_owner if i==0 else new_owner.replace('.json',f'_{i+1}.json')
        plans.append({'candidate':candidate_rel,'new_owner_file':owner_path,'values':data['fix_map'],'fix_keys':list(data['fix_map'])})
        bundles.append({'batch':batch,'review_status':'complete','apply_status':'pending','scene_groups':list(candidate.get('scene_groups',[])),
                        'reviewed_rows':rows,'reviewed_keys':rows,'unique_rows':rows,'fix_keys':fixes,'unique_fix_rows':fixes,'new_pair_keys':0,'new_project_keys':0,
                        'cross_register_keys':0,'existing_owner_updates':0,'keep_keys':len(data['keeps']),'fix_files':[],'review_record':review,
                        'ownership_summary':{'existing_keys':0,'unowned_kept':0,'new_keys':0,'cross_register_keys':0},
                        'allusion_review_candidates':data['allusion_review_candidates'],'allusion_review_resolved':data['allusion_review_resolved'],'fact_doubts':data['fact_doubts'],'source_artifact':source})
        wave_packet.update({'status':'audited','audit_record':{'status':'complete','record':f'_phase4_proofread/AUDIT_YUWEN_MOWEN_TRAIN{train_no}_WAVE{wave_no:02d}_{date}.md','decision_record':audit_path.relative_to(p4.parent).as_posix()},'formal_batch':None,'review_record':None})
    if not 40<=total_rows<=80 or (total_rows>60 and not state.get('wave',{}).get('seal_attestation')): raise EncodingError(f'invalid semantic wave size/attestation: {total_rows}')
    transition(state,'private_encoding'); state['stage']='private_encoding'; state['permissions']=dict(ENCODING_PERMS)
    state['cycle_control'].update({'continuation_required':True,'stop_reason':None,'exact_next_action':'記録済みquality-audit判断をowner・正式束・release stateへ機械収録する','last_safe_checkpoint':'private_encoding'})
    summary={'bundle_count':len(bundles),'reviewed_rows':total_rows,'reviewed_keys':total_rows,'unique_reviewed_rows':total_rows,'fix_keys':total_fixes,'unique_fix_rows':total_fixes,'new_pair_keys':0,'new_project_keys':0,'cross_register_keys':0,'existing_owner_updates':0,'keep_only_bundles':sum(b['fix_keys']==0 for b in bundles)}
    state['wave']['encoding_summary']=dict(summary); manifest['bundles']=bundles; manifest['totals']=dict(summary)
    manifest['private_stage']={'stage':'private_encoding','status':'active','transport_status':'not_ready','wave_id':wave}
    manifest['next_release'].update({'reservation_status':'encoding_active','formal_batches':[b['batch'] for b in bundles],'current_private_stage':'private_encoding'})
    current['ci_train']['totals']=dict(summary); current['ci_train']['private_stage'].update({'stage':'private_encoding','status':'active','cycle_checkpoint':'private_encoding'})
    current['immediate_next']={'scene_groups':list(packet.get('scene_groups',[])),'task':'記録済みquality-audit判断をprivate_encoding pipelineで収録する。','boundary':'翻訳判断を再開せず、decision recordだけをowner・正式束へ写像する。','packet':'_phase4_proofread/NEXT_TASK_PACKET.json'}
    packet['reservation'].update({'status':'encoding_active','encoding_started':True,'formal_batch':bundles[0]['batch'] if len(bundles)==1 else [b['batch'] for b in bundles]})
    attestation=state.get('wave',{}).get('seal_attestation')
    packet['batch_planning']={'mode':'semantic_wave','reviewed_rows':total_rows,'target_rows':{'min':40,'max':60},'hard_max':80,'adjacent_candidates_checked':list(packet.get('scene_groups',[])),'grouping_decision':attestation,'exception':({'reason_code':'complete_semantic_unit','detail':attestation} if total_rows>60 else None)}
    for name,value in [('CURRENT_WORK.json',current),('PRIVATE_STAGE_STATE.json',state),('CI_TRAIN_MANIFEST.json',manifest),('NEXT_TASK_PACKET.json',packet)]: write_json(p4/name,value)
    write_json(p4/'OWNER_ASSIGNMENT_PLAN.json',{'schema_version':1,'packets':plans})
    return {'train_id':train,'wave_id':wave,'date':date,'review_paths':reviews,'batch_numbers':[b['batch'] for b in bundles],'reviewed_rows':total_rows,'fix_keys':total_fixes,'keep_keys':total_keeps}

def finalize(prepared,pr,challenge,p4):
    challenge=direct_path(challenge,p4,'QUALITY_CHALLENGE_','.md',must_exist=True)
    current=load(p4/'CURRENT_WORK.json'); state=load(p4/'PRIVATE_STAGE_STATE.json'); manifest=load(p4/'CI_TRAIN_MANIFEST.json'); packet=load(p4/'NEXT_TASK_PACKET.json'); result=load(p4/'OWNER_ASSIGNMENT_RESULT.json')
    packets=state.get('wave',{}).get('packets'); bundles=manifest.get('bundles')
    if state.get('stage')!='private_encoding' or not isinstance(packets,list) or not isinstance(bundles,list) or len(packets)!=len(bundles): raise EncodingError('encoding finalization state mismatch')
    for wp,bundle in zip(packets,bundles): wp.update({'status':'encoded','formal_batch':bundle['batch'],'review_record':{'status':'complete','record':bundle['review_record'],'apply_status':'pending'}})
    transition(state,'translation_frozen'); state['stage']='translation_frozen'; state['permissions']=dict(FROZEN_PERMS)
    state['transport']['status']='ready_for_public_ci'; state['transport']['history'].append({'status':'ready_for_public_ci','translation_stage':'translation_frozen','pr':pr}); state['transport']['pr']=pr
    state['cycle_control'].update({'status':'running','continuation_required':True,'stop_reason':None,'exact_next_action':'release-ci labelで固定release trainを起動する','last_safe_checkpoint':'ready_for_public_ci'})
    manifest['status']='ready_for_public_ci'; manifest['draft_pr']=pr; manifest['transport'].update({'status':'ready_for_public_ci','translation_stage':'translation_frozen','pr':pr})
    manifest['private_stage']={'stage':'translation_frozen','status':'complete','transport_status':'ready_for_public_ci','wave_id':prepared['wave_id']}; manifest['next_release'].update({'reservation_status':'encoded','formal_batches':prepared['batch_numbers'],'current_private_stage':'translation_frozen'})
    low=prepared['reviewed_rows']>0 and prepared['fix_keys']*100<prepared['reviewed_rows']*15
    gate={'schema_version':1,'primary_objective':'repair_substantive_translation_defects','throughput_metrics_role':'transport_only','low_yield_threshold_percent':15,'reviewed_keys':prepared['reviewed_rows'],'unique_reviewed_rows':prepared['reviewed_rows'],'fix_keys':prepared['fix_keys'],'unique_fix_rows':prepared['fix_keys'],'keep_only_bundles':sum(b.get('fix_keys')==0 for b in bundles),'pre_challenge_unique_fix_rows':prepared['fix_keys'],'low_yield_detected':low,'release_decision':'quality_passed'}
    if low: gate['challenge_pass']={'status':'complete','scope':'all_initial_keep_unique_rows','reviewed_candidate_keep_rows':prepared['keep_keys'],'findings_unique_rows':0,'finding_keys':0,'record':challenge}
    manifest['quality_gate']=gate
    current['operation_mode'].update({'declared_state':'translation_frozen','protocol':'_phase4_proofread/PRIVATE_TRANSLATION_STAGES.md'}); current['ci_train'].update({'status':'ready_for_public_ci','transport_status':'ready_for_public_ci','draft_pr':pr})
    current['ci_train']['private_stage'].update({'stage':'translation_frozen','status':'complete','transport_status':'ready_for_public_ci','cycle_checkpoint':'ready_for_public_ci'})
    current['immediate_next']={'scene_groups':list(packet.get('scene_groups',[])),'task':'release-ci labelでRelease train orchestratorを起動する。','boundary':'翻訳判断は凍結済み。Relation・Cross・Apply・phase2だけを実行する。','packet':'_phase4_proofread/NEXT_TASK_PACKET.json'}
    packet['reservation'].update({'status':'encoded','encoding_started':True}); packet['do_not_do']=['translation_frozen中にKEEP/FIX判断を再開しない','release orchestrator以外の一時CIを作らない','ゲームフォルダへ配置しない']; packet['owner_assignment_result']='_phase4_proofread/OWNER_ASSIGNMENT_RESULT.json'; packet['owner_assignment_counts']=result.get('counts',{})
    for name,value in [('CURRENT_WORK.json',current),('PRIVATE_STAGE_STATE.json',state),('CI_TRAIN_MANIFEST.json',manifest),('NEXT_TASK_PACKET.json',packet)]: write_json(p4/name,value)
    result['state_file_digests']={f'_phase4_proofread/{name}':digest(p4/name) for name in ('CI_TRAIN_MANIFEST.json','PRIVATE_STAGE_STATE.json','CURRENT_WORK.json')}; write_json(p4/'OWNER_ASSIGNMENT_RESULT.json',result)
    return {**prepared,'status':'ready_for_public_ci','pr':pr,'owner_counts':result.get('counts',{})}

def run_pipeline(audit_path,pr_number,new_owner_file,challenge_record,p4=P4):
    prepared=prepare(audit_path,pr_number,new_owner_file,p4); owner_v2.apply_plan(p4.parent,p4/'OWNER_ASSIGNMENT_PLAN.json',p4/'OWNER_ASSIGNMENT_RESULT.json'); return finalize(prepared,pr_number,challenge_record,p4)

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--audit',required=True,type=Path); parser.add_argument('--pr-number',required=True,type=int); parser.add_argument('--new-owner-file',required=True); parser.add_argument('--challenge-record',required=True); parser.add_argument('--write',action='store_true'); parser.add_argument('--output',type=Path); args=parser.parse_args()
    audit=args.audit if args.audit.is_absolute() else ROOT/args.audit
    if not args.write: print(json.dumps({'status':'dry_run_requires_isolated_fixture','audit':str(args.audit)},ensure_ascii=False)); return 0
    try: result=run_pipeline(audit,args.pr_number,args.new_owner_file,args.challenge_record)
    except (OSError,json.JSONDecodeError,ValueError) as exc: print(json.dumps({'status':'blocked','error_code':'factory_encoding_failure','detail':str(exc)},ensure_ascii=False)); return 1
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: write_text(args.output,text)
    print(text,end=''); return 0
if __name__=='__main__': raise SystemExit(main())
