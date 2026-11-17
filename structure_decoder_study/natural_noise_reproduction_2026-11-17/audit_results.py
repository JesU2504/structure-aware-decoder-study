"""Independent saved-result and sampler-provenance audit. No decoder calls."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from statistics import NormalDist

import numpy as np
import scipy.sparse as sp
import stim

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
ENTRY=ROOT/"entry"


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def digest(array):
    return hashlib.sha256(array.tobytes()).hexdigest()


def save(p,value):
    p.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def wilson(k,n):
    z=NormalDist().inv_cdf(0.975)
    phat=k/n
    center=(phat+z*z/(2*n))/(1+z*z/n)
    radius=z*np.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/(1+z*z/n)
    return [float(center-radius),float(center+radius)]


def main():
    frozen,result=read(ROOT/"frozen.json"),read(ROOT/"run_result.json")
    assert result["status"]=="completed"
    assert sha(ROOT/"frozen.json")==result["frozen_sha256"]
    for name,expected in frozen["files"].items():
        assert sha(Path(name))==expected,name
    assert read(ROOT/"pre_run_audit.json")["passed"]
    assert read(ROOT/"adapter_result.json")["passed"]
    gate=read(ENTRY/"result.json")
    assert gate["status"]=="pass" and all(gate["checks"].values())
    h,l=sp.load_npz(ENTRY/"H.npz"),sp.load_npz(ENTRY/"L.npz")
    shots=np.load(ROOT/"shots.npz")
    jobs=read(ROOT/"jobs.json")
    events=[json.loads(line) for line in (ROOT/"invocations.jsonl").read_text().splitlines()]
    rows=[r for r in events if r["event"]=="complete"]
    starts=[r for r in events if r["event"]=="decode_start"]
    attempts=[r for r in events if r["event"]=="start"]
    assert len(rows)==len(starts)==len(attempts)==result["decoder_calls_started"]==result["decoder_calls_completed"]==1627
    assert [r["index"] for r in rows]==[r["index"] for r in starts]==list(range(len(rows)))
    assert len(rows)<frozen["limits"]["invocations"] and result["incomplete_decode_calls"]==0
    assert result["cpu_seconds"]<frozen["limits"]["cpu_seconds"] and result["wall_seconds"]<frozen["limits"]["wall_seconds"]
    main_rows=[r for r in rows if r["phase"]=="main"]
    assert len(main_rows)==len(jobs)==1536
    main_by={(r["case_id"],r["config"]["name"]):r for r in main_rows}
    assert len(main_by)==1536
    for r,job in zip(main_rows,jobs):
        assert r["case_id"]==job["case_id"] and r["config"]==frozen["configs"][job["config_index"]]
        assert not r["fresh_instance"]
        assert r["first_call_in_block"]==(r["case_id"]%256==0)

    replay_count=forced_count=nonfinite_llr_calls=0
    for r in rows:
        p=ROOT/"calls"/f"{r['index']:04d}"
        saved=read(p.with_suffix(".json"))
        data=np.load(p.with_suffix(".npz"))
        correction,bp=data["correction"],data["bp"]
        assert digest(correction)==r["correction_sha256"] and digest(bp)==r["bp_sha256"]
        assert np.isin(correction,[0,1]).all() and np.isin(bp,[0,1]).all()
        nonfinite_llr_calls+=int(not np.isfinite(data["llrs"]).all())
        if r["phase"]=="adapter_toy":
            hm=np.array([[1,1,0],[0,1,1]],dtype=np.uint8)
            lm=np.array([[1,1,1]],dtype=np.uint8)
        else:
            hm,lm=h,l
        predicted_s=np.asarray(hm@correction).ravel()%2
        predicted_l=np.asarray(lm@correction).ravel()%2
        bad_s=int(np.count_nonzero(predicted_s!=data["syndrome"]))
        bad_l=int(np.count_nonzero(predicted_l!=data["actual"]))
        outcome="invalid_correction" if bad_s else "logical_failure" if bad_l else "correct"
        assert r["syndrome_residual"]==bad_s and r["logical_difference"]==bad_l and r["outcome"]==outcome
        assert np.array_equal(predicted_l,data["predicted"])
        assert np.array_equal(correction,data["source_readout"]) and r["source_readout_equal"]
        if not r["zero_syndrome"] and r["bp_converged"]:
            assert np.array_equal(np.asarray(hm@bp).ravel()%2,data["syndrome"])
            if not r["config"]["force"]:
                assert np.array_equal(bp,correction)
        if isinstance(r["case_id"],int):
            i=r["case_id"]
            assert np.array_equal(data["syndrome"],shots["syndrome"][i])
            assert np.array_equal(data["actual"],shots["actual"][i])
        if r["phase"]=="replay":
            replay_count+=1
            previous=main_by[r["case_id"],r["config"]["name"]]
            for key in ("outcome","correction_sha256","bp_sha256","bp_converged","bp_iterations"):
                assert r[key]==previous[key],(r["index"],key)
            assert r["fresh_instance"]
        if r["phase"]=="forced":
            forced_count+=1
        if r["config"]["force"] and not r["zero_syndrome"]:
            stats=saved["statistics"]
            assert r["postprocessing_observed"] and len(stats["individual_cluster_stats"])>0
            assert stats["lsd_order"]==r["config"]["order"]
    assert replay_count==48 and forced_count==32

    failed=[i for i in range(512) if main_by[i,"osd20"]["outcome"]!="correct"][:8]
    successes=[i for i in range(512) if main_by[i,"osd20"]["outcome"]=="correct"]
    expected_pairs=[];used=set()
    for i in failed:
        pool=[j for j in successes if j not in used]
        # Recompute matching from saved syndrome arrays, independently of row weights.
        j=sorted(pool,key=lambda j:(shots["seed"][j]!=shots["seed"][i],
            abs(int(shots["syndrome"][j].sum())-int(shots["syndrome"][i].sum())),j))[0]
        expected_pairs.append((i,j));used.add(j)
    pairs=read(ROOT/"selected_pairs.json")
    assert [(r["failure"],r["control"]) for r in pairs]==expected_pairs
    assert result["selected_cases"]==[i for pair in expected_pairs for i in pair]

    circuit=stim.Circuit.from_file(ENTRY/"bb144_r24_p0.007_z.stim")
    regenerated=[]
    for block,seed in enumerate(frozen["seeds"]):
        d,o=circuit.compile_detector_sampler(seed=seed).sample(256,separate_observables=True)
        assert np.array_equal(d,shots["syndrome"][block*256:(block+1)*256])
        assert np.array_equal(o,shots["actual"][block*256:(block+1)*256])
        regenerated.append(dict(seed=seed,shots=256,syndrome_sha256=digest(d.astype(np.uint8)),actual_sha256=digest(o.astype(np.uint8))))
    save(ROOT/"sampler_regeneration_audit.json",dict(passed=True,blocks=regenerated,
        interpretation="Deterministic regeneration of the same 512 observations, not 512 new independent samples"))

    statistics={}
    for cfg in frozen["configs"]:
        subset=[r for r in main_rows if r["config"]==cfg]
        logical=sum(r["outcome"]=="logical_failure" for r in subset)
        invalid=sum(r["outcome"]=="invalid_correction" for r in subset)
        assert result["counts"][cfg["name"]]==dict(correct=512-logical-invalid,logical_failure=logical,invalid_correction=invalid)
        statistics[cfg["name"]]=dict(logical_errors=logical,invalid_corrections=invalid,n=512,
            logical_error_fraction=logical/512,marginal_wilson95=wilson(logical,512),
            per_seed=[dict(seed=seed,n=256,logical_errors=sum(r["outcome"]=="logical_failure" and r["case_id"]//256==block for r in subset)) for block,seed in enumerate(frozen["seeds"])],
            bp_nonconverged=sum(not r["bp_converged"] for r in subset),
            bp_nonconverged_but_full_correct=sum(not r["bp_converged"] and r["outcome"]=="correct" for r in subset),
            median_service_ms=float(np.median([r["decode_wall_ns"] for r in subset]))/1e6,
            mean_service_ms=float(np.mean([r["decode_wall_ns"] for r in subset]))/1e6,
            main_initialization_ms=[r["wall_ns"]/1e6 for r in events if r["event"]=="construction" and str(r["label"]).startswith("block_") and r["config"]==cfg])
    transitions={}
    for name in ("lsd30","lsd100"):
        transitions[name]=dict(primary_error_control_correct=0,primary_correct_control_error=0,both_correct=0,both_error=0,changed_corrections=0)
        for i in range(512):
            a,b=main_by[i,"osd20"],main_by[i,name]
            ca,cb=a["outcome"]=="correct",b["outcome"]=="correct"
            key="both_correct" if ca and cb else "primary_error_control_correct" if not ca and cb else "primary_correct_control_error" if ca and not cb else "both_error"
            transitions[name][key]+=1
            transitions[name]["changed_corrections"]+=int(a["correction_sha256"]!=b["correction_sha256"])
    selected_set=set(result["selected_cases"])
    forced_transitions={}
    for cfg in frozen["forced_configs"]:
        subset=[r for r in rows if r["phase"]=="forced" and r["config"]==cfg]
        assert len(subset)==len(selected_set)==16
        forced_transitions[cfg["name"]]=dict(selected_cases=16,primary_failures_selected=8,
            primary_error_forced_correct=sum(main_by[r["case_id"],"osd20"]["outcome"]!="correct" and r["outcome"]=="correct" for r in subset),
            primary_correct_forced_error=sum(main_by[r["case_id"],"osd20"]["outcome"]=="correct" and r["outcome"]!="correct" for r in subset),
            correct=sum(r["outcome"]=="correct" for r in subset),
            mean_service_ms=float(np.mean([r["decode_wall_ns"] for r in subset]))/1e6,
            scope="Only first-selected failures and matched primary successes; not all 512 shots")

    previous={}
    paths=list(read(STUDY/"failure_pilot_2026-11-17/result_audit.json")["previous_manifests_verified"])
    paths.append("failure_pilot_2026-11-17/manifest.json")
    for name in paths:
        manifest=STUDY/name
        files=read(manifest)["files"]
        for relative,expected in files.items():
            assert sha(manifest.parent/relative)==expected,(name,relative)
        previous[name]=len(files)

    # Export first independently checked logical-error packet with its inputs.
    first=next(i for i in range(512) if main_by[i,"osd20"]["outcome"]=="logical_failure")
    assert first in selected_set
    packet=ROOT/"witness_packet"
    assert not packet.exists(),"Preserve a prior packet export"
    packet.mkdir()
    input_names=["H.npz","L.npz","priors.npy","bb144_r24_p0.007_z.stim","bb144_r24_p0.007_z.dem"]
    for name in input_names:
        shutil.copyfile(ENTRY/name,packet/name)
    packet_rows=[r for r in rows if r["case_id"]==first]
    for r in packet_rows:
        for suffix in (".json",".npz"):
            shutil.copyfile(ROOT/"calls"/f"{r['index']:04d}{suffix}",packet/f"{r['index']:04d}{suffix}")
    np.savez_compressed(packet/"observation.npz",syndrome=shots["syndrome"][first],actual=shots["actual"][first])
    save(packet/"packet.json",dict(case_id=first,seed=int(shots["seed"][first]),within_seed=int(shots["within_seed"][first]),
        primary=main_by[first,"osd20"],included_calls=packet_rows,source_commit=read(ROOT/"source_manifest.json")["commit"],
        versions=frozen["versions"],python=frozen["python"],common_decoder_settings=dict(bp_method="ms",ms_scaling_factor=0.625,schedule="parallel",omp_thread_count=1,random_schedule_seed=0,input_vector_type="syndrome"),
        files={p.name:sha(p) for p in sorted(packet.iterdir()) if p.is_file()},
        notes="Cached physical-shot syndrome/logical labels; no unique raw/merged/physical fault support is asserted. Native primary failure is syndrome-valid and was replayed on a fresh instance."))
    audit=dict(passed=True,decoder_calls=1627,adapter_calls=11,main_calls=1536,fresh_replay_calls=48,
        forced_comparison_calls=32,incomplete_calls=0,natural_circuit_samples=512,deterministically_regenerated_same_samples=512,
        new_decoder_calls_during_audit=0,nonfinite_llr_calls=nonfinite_llr_calls,
        all_source_native_readouts_equal=True,all_selected_fresh_replays_equal=True,
        marginal_configuration_statistics=statistics,native_paired_transitions=transitions,selected_forced_transitions=forced_transitions,
        witness_packet_case=first,previous_manifests_verified=previous,source_hashes_unchanged=True,
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)),
        interpretation="Replication of source Z-check-only memory; marginal intervals and paired descriptive results, not novel method or decoder-superiority evidence")
    save(ROOT/"result_audit.json",audit)
    print(json.dumps({k:v for k,v in audit.items() if k not in ("previous_manifests_verified","marginal_configuration_statistics")}))
    print(json.dumps(statistics))


if __name__=="__main__":
    main()
