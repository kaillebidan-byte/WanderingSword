#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixed bootstrap from a merged pair-completion checkpoint to the next pair inventory."""
from __future__ import annotations
import argparse, copy, json, re, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent; P4=ROOT/"_phase4_proofread"
CONTRACT_ID="pair-inventory-bootstrap-v1"; EXPECTED_ACTION="resume_recorded_checkpoint"
SENTINEL="__PAIR_COMPLETE__"; PAIR_SENTINEL=SENTINEL; SHA=re.compile(r"^[0-9a-f]{40}$"); DIGEST=re.compile(r"^sha256:[0-9a-f]{64}$")

class BootstrapError(ValueError): pass
def load(path:Path)->dict[str,Any]:
    v=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise BootstrapError(f"object required: {path}")
    return v
load_object=load

def save(path:Path,v:dict[str,Any])->None:
    path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def text(v:Any,label:str)->str:
    if not isinstance(v,str) or not v.strip(): raise BootstrapError(f"{label} required")
    return v.strip()
def slist(v:Any,label:str)->list[str]:
    if not isinstance(v,list) or not v or any(not isinstance(x,str) or not x for x in v) or len(v)!=len(set(v)):
        raise BootstrapError(f"{label} must be unique strings")
    return list(v)
def pair(rel:dict[str,Any])->str:
    try: return f"{rel['left']['name']}↔{rel['right']['name']}"
    except (KeyError,TypeError): raise BootstrapError("canonical pair missing")
def next_pair(audit:dict[str,Any],cluster:str,done:str)->str:
    item=next((x for x in audit.get("queue",[]) if isinstance(x,dict) and x.get("id")==cluster),None)
    if not item: raise BootstrapError("cluster missing")
    pairs=slist(item.get("pairs"),"cluster pairs")
    try: i=pairs.index(done)
    except ValueError: raise BootstrapError("completed pair absent from queue")
    if i+1>=len(pairs): raise BootstrapError("no next pair")
    return pairs[i+1]
def request_data(req:dict[str,Any])->dict[str,Any]:
    if req.get("schema_version")!=1 or req.get("contract_id")!=CONTRACT_ID: raise BootstrapError("contract mismatch")
    if req.get("expected_controller_action")!=EXPECTED_ACTION: raise BootstrapError("controller action mismatch")
    prev=text(req.get("previous_pair"),"previous_pair"); nxt=text(req.get("next_pair"),"next_pair")
    rel=req.get("relation")
    if not isinstance(rel,dict) or pair(rel)!=nxt: raise BootstrapError("relation pair mismatch")
    rid=text(rel.get("id"),"relation.id")
    if not re.fullmatch(r"[a-z0-9_]+",rid): raise BootstrapError("relation id invalid")
    for side in ("left","right"):
        if not isinstance(rel.get(side),dict): raise BootstrapError(f"{side} invalid")
        text(rel[side].get("name"),f"{side}.name"); slist(rel[side].get("aliases"),f"{side}.aliases")
    for k in ("left_to_right_markers","right_to_left_markers","direct_exchange_inventory_markers","notes","audit_questions"):
        slist(rel.get(k),k)
    if rel.get("status")!="extracting": raise BootstrapError("relation status must be extracting")
    out=req.get("output",{}); rec=Path(text(out.get("record"),"output.record"))
    if rec.is_absolute() or ".." in rec.parts or rec.parent.as_posix()!="_phase4_proofread" or not rec.name.startswith("PAIR_INVENTORY_") or rec.suffix!=".json":
        raise BootstrapError("output path invalid")
    date=text(req.get("date"),"date")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",date): raise BootstrapError("date invalid")
    return {"prev":prev,"next":nxt,"rel":copy.deepcopy(rel),"rid":rid,"record":rec,"date":date}
def authorities(root:Path):
    p=root/"_phase4_proofread"
    return tuple(load(p/n) for n in ("CURRENT_WORK.json","PRIVATE_STAGE_STATE.json","CI_TRAIN_MANIFEST.json","NEXT_TASK_PACKET.json","audit_status.json","relation_audit_queue.json"))
def validate(cur,st,man,pkt,audit,queue,d):
    if cur.get("current_pair")!=d["prev"] or pkt.get("current_pair")!=d["prev"]: raise BootstrapError("completed pair mismatch")
    if cur.get("checkpoint",{}).get("status")!="verified": raise BootstrapError("checkpoint not verified")
    tr=(cur.get("ci_train",{}).get("transport_status"),st.get("transport",{}).get("status"),man.get("transport",{}).get("status"))
    if tr!=("merged","merged","merged"): raise BootstrapError("merged transport required")
    ctl=st.get("cycle_control",{})
    if (ctl.get("status"),ctl.get("stop_reason"),ctl.get("last_safe_checkpoint"))!=("paused","pair_scope_exhausted","merged_pair_complete"):
        raise BootstrapError("paused merged_pair_complete required")
    comp=pkt.get("pair_completion",{})
    if comp.get("status")!="complete" or comp.get("pair")!=d["prev"] or pkt.get("scene_groups")!=[SENTINEL]:
        raise BootstrapError("pair completion mismatch")
    expected=next_pair(audit,text(cur.get("current_cluster"),"current_cluster"),d["prev"])
    if d["next"]!=expected: raise BootstrapError(f"not deterministic: {expected}")
    items=queue.get("items",[])
    active=next((x for x in items if isinstance(x,dict) and x.get("id")==queue.get("current")),None)
    if not active or pair(active)!=d["prev"]: raise BootstrapError("relation queue current mismatch")
    if any(isinstance(x,dict) and x.get("id")==d["rid"] for x in items): raise BootstrapError("relation id exists")
    if audit.get("pair_status",{}).get(d["next"],{}).get("evidence_inventory")=="complete": raise BootstrapError("inventory already complete")
def prepare(root:Path,req_path:Path):
    d=request_data(load(req_path)); cur,st,man,pkt,audit,queue=authorities(root); validate(cur,st,man,pkt,audit,queue,d)
    for x in queue["items"]:
        if isinstance(x,dict) and x.get("id")==queue.get("current"): x["status"]="high_confidence_pass_complete"
    queue["items"].append(d["rel"]); queue["current"]=d["rid"]; save(root/"_phase4_proofread/relation_audit_queue.json",queue)
    return {"relation_id":d["rid"],"next_pair":d["next"],"record_path":d["record"].as_posix()}
def counts(report:dict[str,Any],rid:str,nxt:str):
    if report.get("schema_version")!=2 or report.get("relation",{}).get("id")!=rid or pair(report["relation"])!=nxt: raise BootstrapError("report identity mismatch")
    c=report.get("counts",{}); keys=("raw_groups","unique_groups","duplicate_groups","direct_exchange_groups","explicit_reference_groups","unique_rows","duplicate_locations")
    if any(not isinstance(c.get(k),int) or c[k]<0 for k in keys): raise BootstrapError("report counts invalid")
    if c["unique_rows"]<1 or c["unique_groups"]<1: raise BootstrapError("report must contain evidence")
    if c["direct_exchange_groups"]+c["explicit_reference_groups"]!=c["unique_groups"] or c["raw_groups"]-c["unique_groups"]!=c["duplicate_groups"]:
        raise BootstrapError("report count identity mismatch")
    if not isinstance(report.get("groups"),list) or len(report["groups"])!=c["unique_groups"]: raise BootstrapError("report groups mismatch")
    return {k:c[k] for k in keys}
def artifact(a):
    if not a.artifact_run or not a.artifact_id or not DIGEST.fullmatch(a.artifact_digest or "") or not SHA.fullmatch(a.artifact_head or ""):
        raise BootstrapError("artifact metadata invalid")
    return {"workflow":"Pair inventory bootstrap","run_id":a.artifact_run,"artifact_id":a.artifact_id,"artifact_name":text(a.artifact_name,"artifact_name"),"artifact_file":f"{a.relation_id}.json","digest":a.artifact_digest,"head_sha":a.artifact_head}
def finalize(root:Path,req_path:Path,report_path:Path,a):
    d=request_data(load(req_path))
    if d["rid"]!=a.relation_id: raise BootstrapError("CLI relation mismatch")
    cur,st,man,pkt,audit,queue=authorities(root)
    rel=next((x for x in queue.get("items",[]) if isinstance(x,dict) and x.get("id")==d["rid"]),None)
    if queue.get("current")!=d["rid"] or not rel or rel.get("status")!="extracting": raise BootstrapError("prepared relation missing")
    report=load(report_path); c=counts(report,d["rid"],d["next"]); art=artifact(a); rel["status"]="inventory_ready"
    record={"schema_version":1,"contract_id":CONTRACT_ID,"date":d["date"],"previous_pair":d["prev"],"next_pair":d["next"],"relation_id":d["rid"],"counts":c,"speaker_inventory":report.get("speaker_inventory",{}),"selection_marker_inventory":report.get("selection_marker_inventory",{}),"direct_exchange_marker_inventory":report.get("direct_exchange_marker_inventory",{}),"source_artifact":art,"primary_evidence_rule":"report rows are primary evidence; persona and relation documents remain subordinate hypotheses","translation_started":False}
    audit.setdefault("pair_status",{})[d["next"]]={"evidence_inventory":"complete","persona_reviewed":"not_started","relation_reviewed":"not_started","translation_reaudited":"not_started","build_verified":"not_started","game_verified":"not_started","evidence":{"raw_blocks":c["raw_groups"],"unique_blocks":c["unique_groups"],"duplicate_blocks":c["duplicate_groups"],"direct_exchange_blocks":c["direct_exchange_groups"],"explicit_reference_blocks":c["explicit_reference_groups"],"unique_rows":c["unique_rows"]},"applied_keys":0,"residual_candidates":"unreviewed","inventory_record":d["record"].as_posix(),"source_artifact":art}
    cluster=text(cur.get("current_cluster"),"current_cluster")
    audit["current"]={"cluster":cluster,"pair":d["next"],"stage":"evidence_inventory","status":"complete","next_action":"factoryのpair namespaceとbranch/output命名を一般化し、最初のsemantic waveを予約する"}
    action=f"{d['next']}のinventory checkpointを確認し、factoryのpair namespaceとbranch/output命名を一般化して最初のsemantic waveを予約する"
    trans={"status":"inventory_ready","previous_pair":d["prev"],"next_pair":d["next"],"relation_id":d["rid"],"inventory_record":d["record"].as_posix(),"source_artifact":art,"translation_started":False}
    st.setdefault("cycle_control",{}).update({"status":"paused","continuation_required":True,"stop_reason":"pair_inventory_bootstrapped","exact_next_action":action,"last_safe_checkpoint":"pair_inventory_ready"}); st["pair_transition"]=copy.deepcopy(trans)
    cur["next_pair_inventory"]=copy.deepcopy(trans); cur["immediate_next"]={"scene_groups":[SENTINEL],"task":action+"。","boundary":"factory一般化と新pair reservationが完了するまで、翻訳準備・判断・owner書込みを開始しない。","packet":"_phase4_proofread/NEXT_TASK_PACKET.json"}
    man["pair_transition"]=copy.deepcopy(trans); pkt["next_pair_inventory"]=copy.deepcopy(trans); pkt["do_not_do"]=["完了済みpairを通常scene reservationへ戻さない","factory一般化前に新pairのsemantic preparationを開始しない","inventory抽出結果だけで人物資料または翻訳判断を確定しない","ゲームフォルダへ配置しない"]
    cp=cur.get("checkpoint",{})
    hand=f"""# 現在の申し送り

> 再開指示: `現状把握して作業の続きを`
>
> 実visibility、open PR、ActionsはGitHub metadataを毎回取得する。

## 現在地

- completed translation pair: `{d['prev']}`
- verified checkpoint: 第{cp.get('batch')}束 / pair {cp.get('pair_applied_keys')} / project {cp.get('project_applied_keys')}
- transport: `merged`
- cycle: `paused / pair_inventory_ready`
- next pair: `{d['next']}`
- relation inventory: `{d['record'].as_posix()}`
- evidence: {c['unique_groups']} unique blocks / {c['unique_rows']} rows
- translation preparation: `not_started`

## exact next action

{action}。

## 禁止

- 完了済みpairを通常scene reservationへ戻さない。
- factory一般化前に新pairの翻訳準備、判断、owner書込みを開始しない。
- inventory抽出結果だけで人物資料を確定しない。
- ゲームフォルダへ配置しない。
"""
    p=root/"_phase4_proofread"
    for n,v in (("relation_audit_queue.json",queue),("audit_status.json",audit),("CURRENT_WORK.json",cur),("PRIVATE_STAGE_STATE.json",st),("CI_TRAIN_MANIFEST.json",man),("NEXT_TASK_PACKET.json",pkt)): save(p/n,v)
    save(root/d["record"],record); (p/"CURRENT_HANDOFF.md").write_text(hand,encoding="utf-8")
    return {"next_pair":d["next"],"counts":c,"record_path":d["record"].as_posix(),"exact_next_action":action}
def args():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--root",type=Path,default=ROOT); p.add_argument("--request",type=Path,required=True)
    m=p.add_mutually_exclusive_group(required=True); m.add_argument("--prepare",action="store_true"); m.add_argument("--finalize",action="store_true")
    p.add_argument("--report",type=Path); p.add_argument("--relation-id"); p.add_argument("--artifact-run",type=int); p.add_argument("--artifact-id",type=int); p.add_argument("--artifact-name"); p.add_argument("--artifact-digest"); p.add_argument("--artifact-head"); p.add_argument("--output",type=Path); return p.parse_args()
def main()->int:
    a=args()
    try:
        req=a.request if a.request.is_absolute() else a.root/a.request
        result=prepare(a.root,req) if a.prepare else finalize(a.root,req,a.report if a.report.is_absolute() else a.root/a.report,a)
    except (OSError,json.JSONDecodeError,BootstrapError,AttributeError) as e:
        print(json.dumps({"status":"blocked","detail":str(e)},ensure_ascii=False)); return 1
    out=json.dumps({"status":"ok",**result},ensure_ascii=False,indent=2)+"\n"
    if a.output: a.output.write_text(out,encoding="utf-8")
    print(out,end=""); return 0
if __name__=="__main__": sys.exit(main())
