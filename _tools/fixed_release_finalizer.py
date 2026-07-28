#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orchestrator finalization artifactからrelease証跡とphase2-ready状態を一括生成する。"""
from __future__ import annotations
import argparse, copy, json, os, re, tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
P4 = ROOT / '_phase4_proofread'
SHA_RE = re.compile(r'^[0-9a-f]{40}$')
TRAIN_RE = re.compile(r'^yuwen-mowen-train-(\d+)$')
RESTART = '現状把握して作業の続きを'

class FinalizerError(ValueError): pass

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict): raise FinalizerError(f'top level must be object: {path}')
    return value

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as h: h.write(text.rstrip()+'\n')
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise

def write_json(path: Path, value: dict[str, Any]) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))

def positive(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0: raise FinalizerError(f'positive integer required: {value!r}')
    return value

def sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value): raise FinalizerError(f'{label} must be lowercase SHA')
    return value

def validate_inputs(request: dict[str, Any], artifact: dict[str, Any], branch: str) -> dict[str, Any]:
    if request.get('schema_version') != 1 or request.get('contract_id') != 'release-finalization-request-v1': raise FinalizerError('request identity mismatch')
    if request.get('operation') != 'finalize_release_state' or request.get('executor') != 'fixed_release_finalizer': raise FinalizerError('request operation/executor mismatch')
    if request.get('branch') != branch: raise FinalizerError('request branch mismatch')
    expected = {k: request.get(k) for k in ('pr','orchestrator_run_id','ci_head','asset_head','apply_changed')}
    if artifact != {'schema_version':1, **expected}: raise FinalizerError('finalization artifact mismatch: {artifact!r} != {expected!r}')
    positive(expected['pr']); positive(expected['orchestrator_run_id']); sha(expected['ci_head'],'ci_head'); sha(expected['asset_head'],'asset_head')
    if expected['apply_changed'] is not True: raise FinalizerError('release finalization requires apply_changed=true')
    return expected

def batch_from_record(path: str) -> int | None:
    m = re.search(r'BATCH(\d+)_', path)
    return int(m.group(1)) if m else None

def next_reservation(current: dict[str, Any], manifest: dict[str, Any], request: dict[str, Any], release_path: str) -> dict[str, Any]:
    next_scene = request.get('next_scene')
    source = request.get('next_source')
    if not isinstance(next_scene, str) or not next_scene: raise FinalizerError('request.next_scene required')
    if not isinstance(source, dict): raise FinalizerError('request.next_source required')
    for key in ('artifact_workflow','artifact_name','artifact_file','artifact_digest','artifact_head','freshness_rule'):
        if not isinstance(source.get(key), str) or not source[key]: raise FinalizerError(f'next_source.{} required')
    positive(source.get('artifact_run')); positive(source.get('artifact_id'))
    checkpoint = current['checkpoint']
    return {
      'schema_version': 6,
      'status': 'ready',
      'task_id': f"post-train{manifest['train_id'].rsplit('-',1)[-1]}-minimal-wave-reservation",
      'based_on_checkpoint': {
        'batch': checkpoint['batch'], 'pair_applied_keys': checkpoint['pair_applied_keys'],
        'project_applied_keys': checkpoint['project_applied_keys'], 'produced_by_pr': checkpoint['produced_by_pr'],
        'release_id': checkpoint['release_identity']['release_id'], 'release_evidence': release_path,
      },
      'current_pair': current['current_pair'], 'scene_groups': [next_scen],
      'reservation': {'status':'reserved_only','wave_id':None,'packet_id':None,'preparation_started':False,'quality_audit_started':False,'encoding_started':False,'formal_batch':None},
      'source': source,
      'release_candidate': {'train_id':manifest['train_id'],'release_id':checkpoint['release_identity']['release_id'],'pr':checkpoint['produced_by_pr'],'status':'verified','merge_sha':None},
      'do_not_do': [
        'minimal reservationのfocus key,voice question,FACT_DOUBT,owner snapshot,batch planningを戻さない',
        f"{manifest['train_id']}統合e��に�next_scen}preparationを開始しない",
        'translation freeze後に翻訳判断,fix追加,owner給更,il式束追加を行わない', 'ゲームフォルダへ配置しない'],
      'ci_train': {'phase':manifest['phase'],'train_id':manifest['train_id'],'manifest':'_phase4_proofread/CI_TRAIN_MANIFEST.json','planned_batch':checkpoint['batch']+1,'post_merge_state_pr_required':False,'single_pr_finalization':True},
    }

def finalize(request: dict[str, Any], artifact: dict[str, Any], *, branch: str, p4: Path=P4) -> dict[str, Any]:
    info = validate_inputs(request, artifact, branch)
    current=load(p4/'CURRENT_WORK.json'); state=load(p4/'PRIVATE_STAGE_STATE.json'); manifest=load(p4/'CI_TRAIN_MANIFEST.json'); audit=load(p4/'audit_status.json')
    pr=info['pr']; run=info['orchestrator_run_id']; ci_head=info['ci_head']; asset_head=info['asset_head']
    train=manifest.get('train_id'); m=TRAIN_RE.fullmatch(str(train))
    if not m or manifest.get('branch') != branch: raise FinalizerError('active train identity mismatch')
    if current.get('ci_train',{}).get('train_id') != train or state.get('train_id') != train: raise FinalizerError('state train mismatch')
    if current.get('ci_train',{}).get('draft_pr') != pr or manifest.get('draft_pr') != pr or state.get('transport',{}).get('pr') != pr: raise FinalizerError('active PR mismatch')
    if state.get('stage') != 'translation_frozen' or manifest.get('status') != 'ready_for_public_ci': raise FinalizerError('finalizer requires frozen ready release')
    bundles=manifest.get('bundles'); totals=manifest.get('totals')
    if not isinstance(bundles,list) or not bundles or not isinstance(totals,dict): raise FinalizerError('formal bundles missing')
    batch=max(positive(b.get('batch')) for b in bundles if isinstance(b,dict))
    pair=current.get('current_pair'); pair_status=audit.get('pair_status',{}).get(pair,{}); latest=audit.get('project',{}).get('latest_build',{})
    pair_keys=positive(pair_status.get('applied_keys')); project_keys=positive(latest.get('applied_keys'))
    records=latest.get('record_index',[])
    applied=[p for p in records if isinstance(p,str) and batch_from_record(p)==batch]
    if len(applied)!=1: raise FinalizerError(f'exactly one applied record required for batch {batch}: {applied}')
    applied_record=applied[0]
    if not (p4.parent/applied_record).is_file(): raise FinalizerError('applied record missing')
    release_id=f'{train}-r1'; release_path=f'_phase4_proofread/RELEASE_EVIDENCE_YUWEN_MOWEN_TRAIN_{m.group(1)}.json'
    notes=request.get('notes',[])
    if not isinstance(notes,list) or any(not isinstance(x,str) or not x for x in notes): raise FinalizerError('request.notes must be string list')
    evidence={'schema_version':2,'status':'verified','release_id':release_id,'train_id':train,'pr':pr,'ci_head':ci_head,'asset_head':asset_head,'applied_record':applied_record,
      'counts':{'batch':batch,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys,'pending_fixes':0},
      'orchestrator':{'id':run,'workflow':'Release train orchestrator','head_sha':ci_head,'event':'pull_request','conclusion':'success'},
      'lineage':{'mode':'branch_ancestor','merge_sha':None},'notes':notes}
    write_json(p4.parent/release_path,evidence)
    current=copy.deepcopy(current); state=copy.deepcopy(state); manifest=copy.deepcopy(manifest)
    current.update({'updated_at':request.get('date'),'state_base_commit':asset_head,'last_completed_batch':batch,'last_reviewed_batch':batch,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys})
    current['checkpoint']={'status':'verified','batch':batch,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys,'produced_by_pr':pr,
      'release_identity':{'kind':'pr_release_v2','release_id':release_id,'evidence':release_path,'pr':pr,'validated_head':asset_head},'applied_record':applied_record}
    scenes=request.get('completed_scenes')
    if not isinstance(scenes,list) or not scenes: scenes=manifest.get('bundles',[{}])[-1].get('scene_groups',[])
    current['immediate_next']={'scene_groups':request.get('next_scene') and [request['next_scene']] or scenes,'task':f'PR #{pr}のfinalize-release phase2と未解決review thread 0件を確認し、検証済みHEADをsquash統合する。','boundary':'translation_frozen後は翻訳判断、fix追加、owner変更、正式束追加を行わない。','packet':'_phase4_proofread/NEXT_TASK_PACKET.json'}
    ci=current['ci_train']; ci.update({'status':'verified','transport_status':'awaiting_private_merge','applied_result':{'orchestrator_run':run,'asset_head':asset_head,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys,'pending_fixes':0,'checkpoint_status':'verified'},
      'verified_result':{'release_id':release_id,'release_evidence':release_path,'record_index_synced':True,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys,'pending_fixes':0},'release_evidence':release_path})
    ci['private_stage'].update({'status':'verified','transport_status':'awaiting_private_merge','cycle_checkpoint':'awaiting_private_merge'})
    current['release_evidence']=release_path
    for bundle in manifest['bundles']:
        bundle['apply_status']='verified'
    manifest.update({'status':'verified','release_evidence':release_path})
    manifest['transport'].update({'status':'awaiting_private_merge','translation_stage':'translation_frozen','pr':pr,'merge_sha':None})
    manifest['private_stage'].update({'status':'verified','transport_status':'awaiting_private_merge'})
    manifest['next_release'].update({'candidate_scene':[request['next_scene']],'reservation_status':'reserved_only','formal_batches':[b['batch'] for b in manifest['bundles']],'current_private_stage':'translation_frozen'})
    state['transport']['status']='awaiting_private_merge'; state['transport']['merge_sha']=None
    existing=[x.get('status') for x in state['transport'].get('history',[]) if isinstance(x,dict)]
    for status in ('in_public_ci','verified','awaiting_private_merge'):
        if status not in existing:
            item={'status':status,'translation_stage':'translation_frozen','pr':pr}
            if status!='in_public_ci': item['release_id']=release_id
            state['transport'].setdefault('history',[]).append(item)
    state['cycle_control'].update({'status':'running','continuation_required':True,'stop_reason':None,'exact_next_action':f'PR #{pr}のfinalize-release phase2とreview thread 0件を確認し、検証済みHEADをsquash mergeする','last_safe_checkpoint':'awaiting_private_merge'})
    state['verified_result']={'release_id':release_id,'evidence':release_path,'ci_head':ci_head,'asset_head':asset_head,'pending_fixes':0}
    for packet in state.get('wave',{}).get('packets',[]):
        if isinstance(packet,dict) and isinstance(packet.get('review_record'),dict): packet['review_record']['apply_status']='verified'
    packet=next_reservation(current,manifest,request,release_path)
    handoff=f'''# 現在の申し送り\n\n> 再開指示: `{RESTART}`\n>\n> 実visibility、未統合PR、GitHub ActionsはGitHub metadataを毎回取得し、この文書の固定値より優先する。\n\n## 現在地\n\n- translation PR #{pr}: phase2検証待ち\n- train: `{train}`\n- verified checkpoint: 第{batch}束 / pair {pair_keys} / project {project_keys}\n- transport: `awaiting_private_merge`\n- cycle: `running / awaiting_private_merge`\n- 次候補: `{request['next_scene']}`（schema v6 minimal reservation）\n\n## 次の作業\n\nfinalize-release phase2と未解決review thread 0件を確認し、検証済みHEADをsquash mergeする。\n\n## 禁止\n\n- phase2成功前にmergeしない。\n- translation freeze後に翻訳判断、fix追加、owner変更、正式束追加を行わない。\n- 次cycleのmode lock前にpreparationを開始しない。\n- ゲームフォルダへ配置しない。\n'''
    for name,value in [('CURRENT_WORK.json',current),('PRIVATE_STAGE_STATE.json',state),('CI_TRAIN_MANIFEST.json',manifest),('NEXT_TASK_PACKET.json',packet)]: write_json(p4/name,value)
    write_text(p4/'CURRENT_HANDOFF.md',handoff)
    return {'status':'awaiting_private_merge','train_id':train,'release_id':release_id,'batch':batch,'pair_applied_keys':pair_keys,'project_applied_keys':project_keys,'release_evidence':release_path,'next_scene':request['next_scene']}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--request',required=True,type=Path); ap.add_argument('--artifact-json',required=True,type=Path); ap.add_argument('--branch-name',required=True); ap.add_argument('--write',action='store_true'); ap.add_argument('--output',type=Path); args=ap.parse_args()
    request=args.request if args.request.is_absolute() else ROOT/args.request; artifact=args.artifact_json if args.artifact_json.is_absolute() else ROOT/args.artifact_json
    if not args.write: print(json.dumps({'status':'dry_run'},ensure_ascii=False)); return 0
    try: result=finalize(load(request),load(artifact),branch=args.branch_name)
    except (OSError,json.JSONDecodeError,ValueError) as exc: print(json.dumps({'status':'blocked','error_code':'factory_release_finalizer_failure",'detail':str(exc)},ensure_ascii=False)); return 1
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: write_text(args.output,text)
    print(text,end=''); return 0
if __name__=='__main__': raise SystemExit(main())
