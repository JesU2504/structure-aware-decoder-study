"""Fresh adversarial test of marginal feature-range sufficiency."""
from pathlib import Path
import argparse,json
import numpy as np
from scipy.stats import beta
from stress import ROOT,assemble,convert,feature_values,predict,save_json,digest,measure,seed,B2
import stim

def interval(k,n,alpha):
    return [0. if k==0 else float(beta.ppf(alpha/2,k,n-k+1)),
            1. if k==n else float(beta.ppf(1-alpha/2,k+1,n-k))]

def prepare():
    assert not (ROOT/"feature_box_config.json").exists()
    original=json.loads((ROOT/"corpus.json").read_text())
    models=json.loads((ROOT/"frozen_models.json").read_text());out=[]
    for program in ("q4_P01","q4_P03"):
        ref=next(r for r in original if r["program"]==program and r["distance"]==5 and r["rounds"]==10 and r["p"]==.001 and r["placement"]=="spread")
        cr=stim.Circuit.from_file(str(ROOT/"circuits"/f"{ref['name']}.stim"));hr,lr,_,_=convert(cr.detector_error_model())
        r={k:ref[k] for k in ("program","distance","rounds","blocks","gates","events","placement","canonical_map","budget_ns")}
        r.update(name=f"{program}_d5_w10_p0_0024_spread",p=.0024,axis="adversarial_feature_box")
        c=assemble(5,4,10,.0024,r["gates"],r["events"]);dem=c.detector_error_model();h,l,p,_=convert(dem)
        assert h.shape==hr.shape and (h!=hr).nnz==0 and (l!=lr).nnz==0 and c.without_noise()==cr.without_noise()
        f=feature_values(5,4,10,h,p);r["features"]=f
        x=np.log1p([f[k] for k in B2]);support=models["support"]
        outside=[k for j,k in enumerate(B2) if x[j]<support["minimum"][j]-1e-10 or x[j]>support["maximum"][j]+1e-10]
        assert not outside,(program,outside)
        r["outside_training_features"]=outside;r["physical_noise_differs_from_training"]=True
        r["predictions"]={target:{name:dict(raw_ns=predict(model,f),padded_ns=predict(model,f)*model["historical_margin"])
                                  for name,model in models[target].items()} for target in ("mean_ns","p95_ns")}
        assert r["predictions"]["p95_ns"]["B2"]["padded_ns"]<r["budget_ns"]
        text=str(c);dt=str(dem);(ROOT/"circuits"/f"{r['name']}.stim").write_text(text);(ROOT/"circuits"/f"{r['name']}.dem").write_text(dt)
        r["circuit_sha256"]=digest(text.encode());r["dem_sha256"]=digest(dt.encode());out.append(r)
        print(json.dumps(dict(prepared=r["name"],padded_p95_ns=r["predictions"]["p95_ns"]["B2"]["padded_ns"],all_inputs_within=True)),flush=True)
    save_json(ROOT/"feature_box_corpus.json",out)
    save_json(ROOT/"feature_box_config.json",dict(date="2026-11-13",sessions=3,shots_per_session=2000,
                  hashes={n:digest((ROOT/n).read_bytes()) for n in ("box_challenge.py","FEATURE_BOX_CHALLENGE.md","feature_box_corpus.json","frozen_models.json","run_config.json")}))

def run():
    cfg=json.loads((ROOT/"feature_box_config.json").read_text())
    for n,h in cfg["hashes"].items():assert digest((ROOT/n).read_bytes())==h,n
    base=json.loads((ROOT/"run_config.json").read_text());base["confirmation_shots"]=2000
    cases=json.loads((ROOT/"feature_box_corpus.json").read_text())
    for session in range(3):
        order=list(cases);np.random.default_rng(seed("feature_box_order",session)).shuffle(order)
        for r in order:
            path=ROOT/"results/feature_box"/f"session_{session}"/f"{r['name']}.json"
            if path.exists():continue
            measure(r,session,"feature_box",base)
            meta=json.loads(path.read_text())
            meta["phase_config_sha256"]=digest((ROOT/"feature_box_config.json").read_bytes())
            save_json(path,meta)

def analyze():
    cases=json.loads((ROOT/"feature_box_corpus.json").read_text());out=[]
    for r in cases:
        values=[];failures=[];censored=False;sessions=[]
        for session in range(3):
            path=ROOT/"results/feature_box"/f"session_{session}"/f"{r['name']}.npz"
            a=np.load(path);meta=json.loads(path.with_suffix(".json").read_text());censored|=meta["censored"]
            values.extend(a["wall_ns"]);failures.extend(a["logical_z_failure"])
            k=int(np.sum(a["wall_ns"]>r["budget_ns"]))
            sessions.append(dict(session=session,shots=len(a["wall_ns"]),misses=k,
                                 interval=interval(k,len(a["wall_ns"]),.05/6)))
        values=np.array(values);n=len(values);k=int(np.sum(values>r["budget_ns"]))
        ci=None if censored else interval(k,n,.05/2)
        out.append(dict(name=r["name"],p=.0024,shots=n,censored=bool(censored),all_B2_inputs_within_old_ranges=True,
                        physical_noise_differs_from_training=True,padded_prediction_ns=r["predictions"]["p95_ns"]["B2"]["padded_ns"],
                        p95_wall_ns=float(np.quantile(values,.95)),miss_probability=k/n,miss_interval=ci,
                        confident_false_admission=(not censored and ci[0]>.05),
                        logical_z_failure_fraction=float(np.mean(failures)),sessions=sessions))
    save_json(ROOT/"results/feature_box_summaries.json",out);print(json.dumps(out,indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["prepare","run","analyze"])
    args=parser.parse_args();globals()[args.action]()
