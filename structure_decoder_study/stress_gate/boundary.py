"""Selected-task noise-boundary exploration. Frozen original predictors."""
from pathlib import Path
import argparse,json,time,importlib.util
import numpy as np
from stress import ROOT,assemble,convert,feature_values,predict,save_json,digest,measure,seed
import stim
_spec=importlib.util.spec_from_file_location("stress_gate_analysis",ROOT/"analyze.py")
_analysis=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_analysis)
probability_interval=_analysis.probability_interval


def prepare():
    assert not (ROOT/"boundary_config.json").exists()
    old=json.loads((ROOT/"corpus.json").read_text())
    models=json.loads((ROOT/"frozen_models.json").read_text());cases=[]
    for program in ("q4_P01","q4_P03"):
        reference=next(r for r in old if r["program"]==program and r["distance"]==5 and r["rounds"]==10 and r["p"]==.001 and r["placement"]=="spread")
        reference_circuit=stim.Circuit.from_file(str(ROOT/"circuits"/f"{reference['name']}.stim"))
        hr,lr,pr,_=convert(reference_circuit.detector_error_model())
        for noise in (.0015,.002,.0025):
            r={k:reference[k] for k in ("program","distance","rounds","blocks","gates","events","placement","canonical_map","budget_ns")}
            r.update(name=f"{program}_d5_w10_p{str(noise).replace('.','_')}_spread",p=noise,axis="selected_noise_boundary")
            c=assemble(5,4,10,noise,r["gates"],r["events"]);dem=c.detector_error_model()
            h,l,p,_=convert(dem)
            assert h.shape==hr.shape and l.shape==lr.shape and (h!=hr).nnz==0 and (l!=lr).nnz==0
            assert c.without_noise()==reference_circuit.without_noise()
            assert not c.without_noise().compile_detector_sampler(seed=1).sample(32,append_observables=True).any()
            r["features"]=feature_values(5,4,10,h,p)
            r["predictions"]={target:{name:dict(raw_ns=predict(model,r["features"]),padded_ns=predict(model,r["features"])*model["historical_margin"])
                                      for name,model in models[target].items()} for target in ("mean_ns","p95_ns")}
            text=str(c);dt=str(dem)
            (ROOT/"circuits"/f"{r['name']}.stim").write_text(text);(ROOT/"circuits"/f"{r['name']}.dem").write_text(dt)
            r["circuit_sha256"]=digest(text.encode());r["dem_sha256"]=digest(dt.encode())
            r["exact_reference_H_L_and_noiseless_circuit"]=True
            cases.append(r)
    save_json(ROOT/"boundary_corpus.json",cases)
    save_json(ROOT/"boundary_config.json",dict(date="2026-11-13",hashes={n:digest((ROOT/n).read_bytes()) for n in
             ("boundary.py","BOUNDARY_PROTOCOL.md","boundary_corpus.json","frozen_models.json","run_config.json")}))
    print(json.dumps(dict(prepared=len(cases),fixed_H_L=True,frozen=True)),flush=True)


def run():
    config=json.loads((ROOT/"boundary_config.json").read_text())
    for n,h in config["hashes"].items():assert digest((ROOT/n).read_bytes())==h
    base=json.loads((ROOT/"run_config.json").read_text())
    cases=json.loads((ROOT/"boundary_corpus.json").read_text())
    for session in range(3):
        ordered=list(cases);np.random.default_rng(seed("boundary_case_order",session)).shuffle(ordered)
        for r in ordered:
            if (ROOT/"results/boundary"/f"session_{session}"/f"{r['name']}.json").exists():continue
            measure(r,session,"boundary",base)


def analyze():
    cases=json.loads((ROOT/"boundary_corpus.json").read_text());out=[]
    for r in cases:
        values=[];failures=[];censored=False;sessions=[]
        for session in range(3):
            path=ROOT/"results/boundary"/f"session_{session}"/f"{r['name']}.npz"
            a=np.load(path);m=json.loads(path.with_suffix(".json").read_text())
            censored|=m["censored"];values.extend(a["wall_ns"]);failures.extend(a["logical_z_failure"])
            k=int(np.sum(a["wall_ns"]>r["budget_ns"]))
            sessions.append(dict(session=session,shots=len(a["wall_ns"]),misses=k,
                                 interval=probability_interval(k,len(a["wall_ns"]),.05/18)))
        values=np.array(values);k=int(np.sum(values>r["budget_ns"]));n=len(values)
        ci=None if censored else probability_interval(k,n,.05/6)
        out.append(dict(name=r["name"],program=r["program"],p=r["p"],shots=n,censored=bool(censored),
                        miss_probability=k/n,miss_interval=ci,
                        classification=("censored" if censored else "below" if ci[1]<.05 else "above" if ci[0]>.05 else "unresolved"),
                        p95_wall_ns=float(np.quantile(values,.95)),mean_wall_ns=float(values.mean()),
                        logical_z_failure_fraction=float(np.mean(failures)),
                        raw_prediction_ns=r["predictions"]["p95_ns"]["B2"]["raw_ns"],
                        padded_prediction_ns=r["predictions"]["p95_ns"]["B2"]["padded_ns"],sessions=sessions))
    save_json(ROOT/"results/boundary_summaries.json",out)
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["prepare","run","analyze"])
    args=parser.parse_args();globals()[args.action]()
