"""Paired post hoc decomposition diagnostic, separate from the frozen pilot."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
import stim
from study import ROOT,make_decoder,convert,seed,save_json,digest

OUT=ROOT/"results"/"component_control"


def split_matrix(h,priors):
    _,labels=connected_components(sp.bmat([[None,h],[h.T,None]],format="csr"),directed=False)
    parts=[]
    for label in sorted(set(labels[:h.shape[0]])):
        rr=np.flatnonzero(labels[:h.shape[0]]==label)
        cc=np.flatnonzero(labels[h.shape[0]:]==label)
        if len(cc):
            local=h[rr,:][:,cc].tocsc()
            parts.append((rr,cc,local,make_decoder(local,priors[cc])))
    return parts


def one(record,session):
    name=record["name"]
    c=stim.Circuit((ROOT/"circuits"/f"{name}.stim").read_text())
    h,l,p,_=convert(c.detector_error_model())
    joint=make_decoder(h,p)
    start=time.perf_counter_ns()
    parts=split_matrix(h,p)
    setup_ns=time.perf_counter_ns()-start
    warm=c.compile_detector_sampler(seed=seed("component_warm",session,name)).sample(32).astype(np.uint8)
    for s in warm:
        joint.decode(s)
        for rr,cc,local,decoder in parts:
            decoder.decode(s[rr])
    shot_seed=seed("component_shots",session,name)
    det,obs=c.compile_detector_sampler(seed=shot_seed).sample(1000,separate_observables=True)
    det=det.astype(np.uint8)
    ns=np.zeros((2,len(det)),dtype=np.int64)
    work=np.zeros((2,len(det)),dtype=np.int64)
    corrections=np.zeros((2,len(det),h.shape[1]),dtype=np.uint8)
    logical_only=np.flatnonzero(np.diff(h.indptr)==0)
    corrections[1,:,logical_only]=(p[logical_only]>.5).astype(np.uint8)[:,None]
    for j,s in enumerate(det):
        sub_syndromes=[np.ascontiguousarray(s[rr]) for rr,_,_,_ in parts]
        for mode in ((0,1) if j%2==0 else (1,0)):
            if mode==0:
                start=time.perf_counter_ns()
                result=joint.decode(s)
                ns[0,j]=time.perf_counter_ns()-start
                corrections[0,j]=result
                work[0,j]=h.nnz*joint.iter
            else:
                for (rr,cc,local,decoder),syndrome in zip(parts,sub_syndromes):
                    start=time.perf_counter_ns()
                    result=decoder.decode(syndrome)
                    ns[1,j]+=time.perf_counter_ns()-start
                    corrections[1,j,cc]=result
                    work[1,j]+=local.nnz*decoder.iter
    failures=[]
    for mode in (0,1):
        assert np.array_equal((h@corrections[mode].T).T%2,det),(name,mode)
        failures.append(np.any((l@corrections[mode].T).T%2!=obs,axis=1))
    failures=np.array(failures)
    check=np.unique(np.r_[np.arange(16),np.argsort(ns[0])[-8:],np.argsort(ns[1])[-8:]])
    dest=OUT/f"session_{session}"
    dest.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dest/f"{name}.npz",latency_ns=ns,bp_nonzero_work=work,logical_z_failure=failures,
                        checkpoint_indices=check,checkpoint_syndromes=det[check],
                        checkpoint_observables=obs[check],checkpoint_corrections=corrections[:,check])
    summary=dict(name=name,session=session,seed=shot_seed,components=len(parts),shots=len(det),split_setup_ns=setup_ns,
                 joint_mean_ns=float(ns[0].mean()),split_mean_ns=float(ns[1].mean()),
                 joint_p95_ns=float(np.quantile(ns[0],.95)),split_p95_ns=float(np.quantile(ns[1],.95)),
                 joint_failures=int(failures[0].sum()),split_failures=int(failures[1].sum()),
                 predictions_differ=int(np.sum(failures[0]!=failures[1])),
                 config_sha256=digest((OUT/"config.json").read_bytes()))
    save_json(dest/f"{name}.json",summary)
    return summary


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    config=dict(protocol_sha256=digest((ROOT/"COMPONENT_CONTROL_PROTOCOL.md").read_bytes()),
                implementation_sha256=digest(Path(__file__).read_bytes()),
                primary_config_sha256=digest((ROOT/"frozen_config.json").read_bytes()),
                sessions=3,shots_per_case=1000,post_hoc=True)
    if (OUT/"config.json").exists():
        assert json.loads((OUT/"config.json").read_text())==config
    else:
        save_json(OUT/"config.json",config)
    records=[r for r in json.loads((ROOT/"corpus.json").read_text()) if r["case"]["blocks"]==4 and r["case"]["family"] in ("fanout","repeated")]
    for session in range(3):
        ordered=list(records)
        np.random.default_rng(seed("component_order",session)).shuffle(ordered)
        for record in ordered:
            path=OUT/f"session_{session}"/f"{record['name']}.json"
            if path.exists():continue
            s=one(record,session)
            print(json.dumps(s),flush=True)
    pooled=[]
    for record in records:
        name=record["name"]
        raw=[np.load(OUT/f"session_{s}"/f"{name}.npz") for s in range(3)]
        times=np.concatenate([r["latency_ns"] for r in raw],axis=1)
        work=np.concatenate([r["bp_nonzero_work"] for r in raw],axis=1)
        failures=np.concatenate([r["logical_z_failure"] for r in raw],axis=1)
        pooled.append(dict(name=name,family=record["case"]["family"],distance=record["case"]["distance"],
                           placement=record["case"]["placement"],
                           joint_mean_ns=float(times[0].mean()),split_mean_ns=float(times[1].mean()),
                           joint_p95_ns=float(np.quantile(times[0],.95)),split_p95_ns=float(np.quantile(times[1],.95)),
                           mean_speedup=float(times[0].mean()/times[1].mean()),
                           mean_bp_work_ratio=float(work[0].mean()/work[1].mean()),
                           joint_failures=int(failures[0].sum()),split_failures=int(failures[1].sum()),
                           outcome_disagreements=int(np.sum(failures[0]!=failures[1]))))
    save_json(OUT/"summary.json",pooled)
    print(json.dumps(dict(complete=True,case_sessions=54,paired_shots=54000,
                         by_family={g:dict(median_speedup=float(np.median([r["mean_speedup"] for r in pooled if r["family"]==g])),
                                           min_speedup=float(min(r["mean_speedup"] for r in pooled if r["family"]==g)),
                                           max_speedup=float(max(r["mean_speedup"] for r in pooled if r["family"]==g)),
                                           outcome_disagreements=sum(r["outcome_disagreements"] for r in pooled if r["family"]==g))
                                    for g in ("fanout","repeated")})),flush=True)


if __name__=="__main__":main()
