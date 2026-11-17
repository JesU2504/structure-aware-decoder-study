"""Frozen-model stress discovery. See PROTOCOL.md; old artifacts are read only."""
from __future__ import annotations
import argparse
from dataclasses import dataclass,asdict
from functools import lru_cache
import hashlib,itertools,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent
os.environ["MPLCONFIGDIR"]="/private/tmp/structure-decoder-stress-mpl"
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[v]="1"
sys.path.insert(0,str(OLD))
from study import convert,seed,save_json,digest,make_decoder,DECODER_CONFIG
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
import stim,tmcbs

B2=["distance","n_detectors","n_faults","nnz","prior_sum","expected_activity"]
B0=["volume","distance"]


@lru_cache(None)
def code(d):return tmcbs.surface_code(d)


@lru_cache(None)
def fragments(d,q,w,p):
    b=tmcbs.make_builder(code(d),q,p,ebits=False)
    for j in range(q):b.initQubits(j)
    head=b.c.copy();rounds=[]
    for r in range(w):
        start=len(b.c)
        b.extractionRound(list(range(q)),firstPass=(r==0))
        rounds.append(b.c[start:])
    start=len(b.c)
    b.measureDataQubits(list(range(q)))
    for j in range(q):
        b.endOfCircuitDetectorsForLogicalMeasurementReadout(j);b.obsOffset(j,j)
    return head,tuple(rounds),b.c[start:]


@lru_cache(None)
def gate_fragment(d,q,p,a,b):
    builder=tmcbs.make_builder(code(d),q,p,ebits=False)
    builder.transversalOp("CX",[a,b])
    return builder.c.copy()


def assemble(d,q,w,p,gates,events,input_bits=None):
    head,rounds,tail=fragments(d,q,w,p)
    c=head.copy()
    if input_bits is not None:
        n=code(d).n
        for block,bit in enumerate(input_bits):
            if bit:c.append("X",[block*(2*n-1)+int(i) for i in np.flatnonzero(code(d).css.lx[0])])
    for r,part in enumerate(rounds):
        c+=part
        for gate,event in zip(gates,events):
            if event==r:c+=gate_fragment(d,q,p,*gate)
    c+=tail
    return c


def linear_map(q,gates):
    a=np.eye(q,dtype=np.uint8)
    for control,target in gates:a[target]^=a[control]
    return a


def canonical_map(a):
    return min(a[np.ix_(perm,perm)].tobytes().hex() for perm in itertools.permutations(range(len(a))))


def gf2inverse(a):
    q=len(a);x=np.c_[a.copy(),np.eye(q,dtype=np.uint8)]
    for j in range(q):
        pivot=j+int(np.flatnonzero(x[j:,j])[0]);x[[j,pivot]]=x[[pivot,j]]
        for k in range(q):
            if k!=j and x[k,j]:x[k]^=x[j]
    assert np.array_equal(x[:,:q],np.eye(q,dtype=np.uint8))
    return x[:,q:]


def generate_programs():
    archived=json.loads((OLD/"corpus.json").read_text())
    used={4:set(),6:set()}
    for r in archived:
        q=r["case"]["blocks"]
        if q in used:used[q].add(canonical_map(linear_map(q,r["gates"])))
    out=[]
    for q,count,length in ((4,8,6),(6,4,8)):
        rng=np.random.default_rng(seed("stress_programs_v1",q))
        while sum(p["blocks"]==q for p in out)<count:
            gates=[]
            while len(gates)<length:
                a,b=rng.choice(q,2,replace=False).tolist()
                if not gates or gates[-1]!=[a,b]:gates.append([a,b])
            adj=np.eye(q,dtype=bool)
            for a,b in gates:adj[a,b]=adj[b,a]=True
            for j in range(q):adj|=adj[:,j,None]&adj[j,None,:]
            if not adj.all():continue
            matrix=linear_map(q,gates);canonical=canonical_map(matrix)
            if canonical in used[q]:continue
            used[q].add(canonical)
            index=sum(p["blocks"]==q for p in out)
            out.append(dict(id=f"q{q}_P{index:02}",blocks=q,gates=gates,
                            logical_map=matrix.tolist(),canonical_map=canonical))
    return out


def configurations(programs):
    cases=[]
    def add(p,d,w,noise,placement,axis):
        k=len(p["gates"])
        events=([w//2]*k if placement=="burst" else np.rint(np.linspace(1,w-2,k)).astype(int).tolist())
        name=f"{p['id']}_d{d}_w{w}_p{str(noise).replace('.','_')}_{placement}"
        cases.append(dict(name=name,program=p["id"],blocks=p["blocks"],gates=p["gates"],
                          canonical_map=p["canonical_map"],distance=d,rounds=w,p=noise,
                          placement=placement,axis=axis,events=events))
    for p in programs:
        if p["blocks"]==6:add(p,5,10,.001,"spread","blocks_and_program")
        else:
            for placement in ("spread","burst"):add(p,5,10,.001,placement,"new_program_and_placement")
            if int(p["id"][-2:])<4:
                for noise in (.0003,.003):add(p,5,10,noise,"spread","noise")
                for w in (5,15):add(p,5,w,.001,"spread","extent")
                for d in (3,7,9):add(p,d,2*d,.001,"spread","distance_and_extent")
    assert len(cases)==48 and len({c["name"] for c in cases})==48
    return cases


def feature_values(d,q,w,h,priors):
    start=time.perf_counter_ns()
    rd=np.asarray(h.sum(axis=1)).ravel();cd=np.diff(h.indptr)
    activation=-.5*np.expm1(h@np.log1p(-2*priors))
    n,labels=connected_components(sp.bmat([[None,h],[h.T,None]],format="csr"),directed=False)
    detcounts=np.bincount(labels[:h.shape[0]],minlength=n)
    incidence=float(np.dot(priors,cd))
    f=dict(distance=d,volume=q*w,n_detectors=h.shape[0],n_faults=h.shape[1],nnz=h.nnz,
           prior_sum=float(priors.sum()),expected_activity=float(activation.sum()),
           components=int(np.count_nonzero(detcounts)),max_arity=int(cd.max()),
           row_degree_variance=float(rd.var()),col_degree_variance=float(cd.var()),
           hyperedge_fraction=float(np.mean(cd>2)),
           weighted_excess_arity=float(np.dot(priors,cd*(cd-1))/max(incidence,1e-30)),
           activation_second_moment=float(np.dot(activation,activation)/max(activation.sum(),1e-30)),
           feature_time_ns=time.perf_counter_ns()-start)
    return f


def fit_ridge(records,y,columns):
    x=np.log1p([[r["features"][c] for c in columns] for r in records])
    center=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-14]=1
    z=(x-center)/scale;ly=np.log(y);intercept=float(ly.mean())
    beta=np.linalg.solve(z.T@z+np.eye(len(columns)),z.T@(ly-intercept))
    return dict(columns=columns,center=center.tolist(),scale=scale.tolist(),beta=beta.tolist(),
                intercept=intercept,alpha=1.0)


def predict(model,features):
    xx=np.log1p([features[c] for c in model["columns"]])
    return float(np.exp(model["intercept"]+((xx-np.array(model["center"]))/np.array(model["scale"]))@np.array(model["beta"])))


def freeze_models():
    records=json.loads((OLD/"corpus.json").read_text())
    summaries={r["name"]:r for r in json.loads((OLD/"results/case_summaries.json").read_text())}
    groups=np.array(["single_or_repeated" if r["case"]["family"] in ("single","repeated")
                     else r["case"]["family"] for r in records])
    models={}
    for target in ("mean_ns","p95_ns"):
        yy=np.array([summaries[r["name"]][target] for r in records])
        models[target]={}
        for name,columns in (("B0",B0),("B2",B2)):
            model=fit_ridge(records,yy,columns)
            pred=np.zeros(len(records))
            for group in sorted(set(groups)):
                train=groups!=group
                local=fit_ridge([r for r,k in zip(records,train) if k],yy[train],columns)
                for j in np.flatnonzero(~train):pred[j]=predict(local,records[j]["features"])
            model["historical_margin"]=float(max(1.,np.max(yy/pred)))
            model["historical_oof_underprediction_max"]=float(np.max(yy/pred))
            models[target][name]=model
    oldx=np.log1p([[r["features"][c] for c in B2] for r in records])
    models["support"]=dict(columns=B2,minimum=oldx.min(axis=0).tolist(),maximum=oldx.max(axis=0).tolist(),
                            center=oldx.mean(axis=0).tolist(),scale=oldx.std(axis=0).tolist(),rows=oldx.tolist())
    models["training_hashes"]={n:digest((OLD/n).read_bytes()) for n in ("corpus.json","results/case_summaries.json")}
    save_json(ROOT/"frozen_models.json",models)
    return models


def validate_fragments():
    results=[]
    for r in json.loads((OLD/"corpus.json").read_text()):
        case=r["case"]
        c=assemble(case["distance"],case["blocks"],case["rounds"],case["p"],r["gates"],r["event_rounds"])
        expected=(OLD/"circuits"/f"{r['name']}.stim").read_text()
        assert str(c)==expected,r["name"]
        results.append(r["name"])
    save_json(ROOT/"fragment_validation.json",dict(literal_matches=results,count=len(results)))
    print(json.dumps(dict(fragment_matches=len(results))),flush=True)


def validate_program(p):
    d=3;q=p["blocks"];w=6;gates=p["gates"]
    events=np.rint(np.linspace(1,w-2,len(gates))).astype(int).tolist()
    matrix=np.array(p["logical_map"],dtype=np.uint8)
    for bits in itertools.product((0,1),repeat=q):
        c=assemble(d,q,w,0.,gates,events,bits)
        assert not c.compile_detector_sampler(seed=1).sample(8).any()
        raw=c.compile_sampler(seed=2).sample(8).astype(np.uint8)
        final=raw[:,-q*code(d).n:].reshape(8,q,code(d).n)
        result=(final@code(d).css.lz.T)[:,:,0]%2
        expected=matrix@np.array(bits,dtype=np.uint8)%2
        assert np.all(result==expected),p["id"]
    # Prove both logical-Pauli images of the gate-only Clifford operation.
    circuit=stim.Circuit()
    for a,b in gates:circuit+=gate_fragment(d,q,0.,a,b).without_noise()
    n=code(d).n;nqubits=q*(2*n-1);circuit.append("I",[nqubits-1])
    tableau=stim.Tableau.from_circuit(circuit)
    inverse=gf2inverse(matrix)
    for basis,operator in (("X",code(d).css.lx[0]),("Z",code(d).css.lz[0])):
        for block in range(q):
            before=stim.PauliString(nqubits);expected=stim.PauliString(nqubits)
            for index in np.flatnonzero(operator):before[block*(2*n-1)+int(index)]=basis
            affected=matrix[:,block] if basis=="X" else inverse[block,:]
            for target in np.flatnonzero(affected):
                for index in np.flatnonzero(operator):expected[int(target)*(2*n-1)+int(index)]=basis
            assert tableau(before)==expected,(p["id"],basis,block)
    return dict(program=p["id"],truth_table_inputs=2**q,gate_only_pauli_images=2*q,passed=True)


def prepare():
    assert not (ROOT/"run_config.json").exists(),"Prepare only before freezing new timing"
    validate_fragments()
    programs=generate_programs();save_json(ROOT/"programs.json",programs)
    semantic=[validate_program(p) for p in programs]
    models=freeze_models();cases=configurations(programs);validation=[]
    for r in cases:
        start=time.perf_counter_ns()
        c=assemble(r["distance"],r["blocks"],r["rounds"],r["p"],r["gates"],r["events"])
        r["assembly_ns"]=time.perf_counter_ns()-start
        start=time.perf_counter_ns();dem=c.detector_error_model();r["dem_ns"]=time.perf_counter_ns()-start
        h,l,p,mapping=convert(dem)
        f=feature_values(r["distance"],r["blocks"],r["rounds"],h,p)
        r["features"]=f
        # All static information is computed before any new timing is collected.
        x=np.log1p([f[col] for col in B2]);sup=models["support"]
        r["outside_training_features"]=[col for j,col in enumerate(B2) if x[j]<sup["minimum"][j]-1e-10 or x[j]>sup["maximum"][j]+1e-10]
        z=(x-np.array(sup["center"]))/np.array(sup["scale"])
        oldz=(np.array(sup["rows"])-np.array(sup["center"]))/np.array(sup["scale"])
        r["nearest_training_distance"]=float(np.linalg.norm(oldz-z,axis=1).min())
        r["predictions"]={target:{name:dict(raw_ns=predict(model,f),padded_ns=predict(model,f)*model["historical_margin"])
                                  for name,model in models[target].items()} for target in ("mean_ns","p95_ns")}
        r["budget_ns"]=r["distance"]*1_000_000
        assert f["components"]==1,(r["name"],f["components"])
        ideal=c.without_noise().compile_detector_sampler(seed=1).sample(32,append_observables=True)
        assert not ideal.any(),r["name"]
        dd,oo,ee=dem.compile_sampler(seed=seed("stress_dem_validation",r["name"])).sample(64,return_errors=True)
        merged=np.zeros((64,h.shape[1]),dtype=np.uint8)
        for j,k in enumerate(mapping):
            if k>=0:merged[:,k]^=ee[:,j]
        assert np.array_equal((h@merged.T).T%2,dd) and np.array_equal((l@merged.T).T%2,oo)
        text=str(c);dtext=str(dem)
        (ROOT/"circuits"/f"{r['name']}.stim").write_text(text)
        (ROOT/"circuits"/f"{r['name']}.dem").write_text(dtext)
        r["circuit_sha256"]=digest(text.encode());r["dem_sha256"]=digest(dtext.encode())
        validation.append(dict(name=r["name"],connected=True,ideal=True,dem_reconstruction=True))
        print(json.dumps(dict(prepared=r["name"],detectors=h.shape[0],mechanisms=h.shape[1])),flush=True)
    save_json(ROOT/"corpus.json",cases)
    save_json(ROOT/"validation.json",dict(program_semantics=semantic,circuits=validation))
    config=dict(date="2026-11-13",sessions=3,discovery_shots=256,confirmation_shots=1000,cpu_cap_ns=20_000_000_000,
                decoder=DECODER_CONFIG,hashes={p:digest((ROOT/p).read_bytes()) for p in
                  ("PROTOCOL.md","stress.py","corpus.json","frozen_models.json","programs.json","fragment_validation.json","validation.json")})
    save_json(ROOT/"run_config.json",config)
    print(json.dumps(dict(prepared_cases=len(cases),programs=len(programs),frozen=True)),flush=True)


def measure(r,session,phase,config):
    text=(ROOT/"circuits"/f"{r['name']}.stim").read_text()
    assert digest(text.encode())==r["circuit_sha256"]
    c=stim.Circuit(text);h,l,p,_=convert(c.detector_error_model());decoder=make_decoder(h,p)
    warm=c.compile_detector_sampler(seed=seed("stress_warm",phase,session,r["name"])).sample(32).astype(np.uint8)
    for s in warm:decoder.decode(s)
    n=config["discovery_shots" if phase=="discovery" else "confirmation_shots"]
    shot_seed=seed("stress_samples",phase,session,r["name"])
    det,obs=c.compile_detector_sampler(seed=shot_seed).sample(n,separate_observables=True)
    det=det.astype(np.uint8);wall=[];cpu=[];iters=[];converge=[];corrections=[]
    for syndrome in det:
        startw=time.perf_counter_ns();startc=time.process_time_ns()
        correction=decoder.decode(syndrome)
        cp=time.process_time_ns()-startc;wa=time.perf_counter_ns()-startw
        wall.append(wa);cpu.append(cp);iters.append(decoder.iter);converge.append(decoder.converge)
        corrections.append(correction.copy())
        if sum(cpu)>config["cpu_cap_ns"]:break
    count=len(wall);det=det[:count];obs=obs[:count]
    corr=np.array(corrections,dtype=np.uint8)
    assert np.array_equal((h@corr.T).T%2,det),r["name"]
    fail=np.any((l@corr.T).T%2!=obs,axis=1)
    idx=np.unique(np.r_[np.arange(min(8,count)),np.argsort(wall)[-8:]])
    folder=ROOT/"results"/phase/f"session_{session}";folder.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(folder/f"{r['name']}.npz",wall_ns=wall,cpu_ns=cpu,bp_iterations=iters,
                        bp_converged=converge,logical_z_failure=fail,syndrome_weight=det.sum(axis=1),
                        checkpoint_indices=idx,checkpoint_detectors=det[idx],checkpoint_observables=obs[idx],
                        checkpoint_corrections=corr[idx])
    summary=dict(name=r["name"],session=session,phase=phase,seed=shot_seed,shots=count,planned_shots=n,
                 censored=(count<n),mean_wall_ns=float(np.mean(wall)),p95_wall_ns=float(np.quantile(wall,.95)),
                 mean_cpu_ns=float(np.mean(cpu)),p95_cpu_ns=float(np.quantile(cpu,.95)),
                 wall_misses=int(np.sum(np.array(wall)>r["budget_ns"])),cpu_misses=int(np.sum(np.array(cpu)>r["budget_ns"])),
                 logical_z_failures=int(fail.sum()),bp_fallback_fraction=float(1-np.mean(converge)),
                 config_sha256=digest((ROOT/"run_config.json").read_bytes()))
    save_json(folder/f"{r['name']}.json",summary)
    print(json.dumps(summary),flush=True)


def run(phase):
    config=json.loads((ROOT/"run_config.json").read_text())
    for name,expected in config["hashes"].items():assert digest((ROOT/name).read_bytes())==expected,name
    cases=json.loads((ROOT/"corpus.json").read_text())
    if phase=="confirmation":
        selected=json.loads((ROOT/"confirmation_selection.json").read_text())
        cases=[r for r in cases if r["name"] in selected["names"]]
    for session in range(config["sessions"]):
        ordered=list(cases);np.random.default_rng(seed("stress_order",phase,session)).shuffle(ordered)
        for r in ordered:
            path=ROOT/"results"/phase/f"session_{session}"/f"{r['name']}.json"
            if path.exists():continue
            measure(r,session,phase,config)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["prepare","discovery","confirmation"])
    args=parser.parse_args()
    if args.action=="prepare":prepare()
    else:run(args.action)
