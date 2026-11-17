"""Reproducible, sector-scoped circuit/decoder entry study. See PROTOCOL.md."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources" / "basilthebeagles-tmcbs-c0490fa"
COMMIT = "c0490fa63965d8984cca89deb8826c19c46e8a3c"
sys.path.insert(0, str(SOURCE))
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
import stim
import tmcbs
from ldpc.bplsd_decoder import BpLsdDecoder


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def seed(namespace: str, *parts) -> int:
    return int.from_bytes(hashlib.sha256(json.dumps([namespace, *parts]).encode()).digest()[:8], "little")


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


PROGRAMS = {
    2: {"memory": [], "single": [(0, 1)], "repeated": [(0, 1)] * 3},
    4: {
        "memory": [], "pairs": [(0, 1), (2, 3)],
        "chain": [(0, 1), (1, 2), (2, 3)],
        "fanout": [(0, 1), (0, 2), (0, 3)],
        "fanin": [(1, 0), (2, 0), (3, 0)],
        "cycle": [(0, 1), (1, 2), (2, 3), (3, 0)],
        "repeated": [(0, 1)] * 3,
    },
}
DECODER_CONFIG = dict(max_iter=30, bp_method="minimum_sum", ms_scaling_factor=0.625,
                      schedule="parallel", lsd_order=0, lsd_method="LSD_0",
                      omp_thread_count=1, random_schedule_seed=0,
                      input_vector_type="syndrome")


@dataclass(frozen=True)
class Case:
    distance: int
    blocks: int
    family: str
    placement: str
    rounds: int = 12
    p: float = 0.001

    @property
    def name(self):
        return f"d{self.distance}_q{self.blocks}_{self.family}_{self.placement}"

    @property
    def gates(self):
        return PROGRAMS[self.blocks][self.family]

    @property
    def event_rounds(self):
        k = len(self.gates)
        if not k:
            return []
        if self.placement == "early":
            return list(range(2, 2 + k))
        if self.placement == "late":
            return list(range(self.rounds - 1 - k, self.rounds - 1))
        if self.placement == "spread":
            if k == 1:
                return [(self.rounds - 1) // 2]
            return [int(x) for x in np.linspace(2, self.rounds - 2, k)]
        raise ValueError(self.placement)


def cases():
    return [Case(d, q, family, placement)
            for d in (3, 5, 7) for q in (2, 4)
            for family, gates in PROGRAMS[q].items()
            for placement in (("none",) if not gates else ("early", "spread", "late"))]


def build(case: Case, *, input_bits=None, noise=None):
    code = tmcbs.surface_code(case.distance)
    p = case.p if noise is None else noise
    b = tmcbs.make_builder(code, case.blocks, p, ebits=False)
    for q in range(case.blocks):
        b.initQubits(q)
        if input_bits is not None and input_bits[q]:
            b.logicalOp("X", code.css.lx[0], q, errors=False)
    events = dict(zip(case.event_rounds, case.gates))
    assert len(events) == len(case.gates)
    for r in range(case.rounds):
        b.extractionRound(list(range(case.blocks)), firstPass=(r == 0))
        if r in events:
            b.transversalOp("CX", list(events[r]))
    b.measureDataQubits(list(range(case.blocks)))
    for q in range(case.blocks):
        b.endOfCircuitDetectorsForLogicalMeasurementReadout(q)
        b.obsOffset(q, q)
    return b.getCirc()


def convert(dem):
    """Exact parity support + XOR merge of independent identical DEM mechanisms.

    The source model itself may approximate physical correlations; this function
    does not introduce a second approximation or sample the converted model.
    """
    supports, probabilities, lookup, error_to_col = [], [], {}, []
    for instruction in dem.flattened():
        if instruction.type != "error":
            if instruction.type not in ("detector", "logical_observable"):
                raise ValueError(instruction.type)
            continue
        ds, ls = set(), set()
        for target in instruction.targets_copy():
            target_set = ds if target.is_relative_detector_id() else ls if target.is_logical_observable_id() else None
            if target_set is not None:
                target_set.symmetric_difference_update((target.val,))
            elif not target.is_separator():
                raise ValueError(str(target))
        support = (tuple(sorted(ds)), tuple(sorted(ls)))
        if not any(support):
            error_to_col.append(-1)
            continue
        prob = instruction.args_copy()[0]
        if support not in lookup:
            lookup[support] = len(supports)
            supports.append(support)
            probabilities.append(prob)
        else:
            j = lookup[support]
            old = probabilities[j]
            probabilities[j] = old + prob - 2 * old * prob
        error_to_col.append(lookup[support])
    n = len(supports)
    def matrix(axis, count):
        rr, cc = [], []
        for j, support in enumerate(supports):
            rr.extend(support[axis])
            cc.extend([j] * len(support[axis]))
        return sp.csc_matrix((np.ones(len(rr), dtype=np.uint8), (rr, cc)), shape=(count, n))
    return (matrix(0, dem.num_detectors), matrix(1, dem.num_observables),
            np.array(probabilities), np.array(error_to_col, dtype=np.int64))


def features(case, h, l, priors):
    t0 = time.perf_counter_ns()
    csr = h.tocsr()
    rd, cd = np.diff(csr.indptr), np.diff(h.indptr)
    expected = 0.5 * (1 - np.array([np.prod(1 - 2 * priors[csr.indices[csr.indptr[i]:csr.indptr[i+1]]])
                                   for i in range(h.shape[0])]))
    adjacency = sp.bmat([[None, h], [h.T, None]], format="csr")
    ncomponents, labels = connected_components(adjacency, directed=False)
    counts = np.bincount(labels)
    detector_counts = np.bincount(labels[:h.shape[0]], minlength=ncomponents)
    active = detector_counts > 0
    # This bounded statistic avoids materializing potentially dense H H^T.
    sample_rows = np.unique(np.linspace(0, max(0, h.shape[0]-1), min(32, h.shape[0]), dtype=int))
    two_step = []
    for row in sample_rows:
        cols = csr.indices[csr.indptr[row]:csr.indptr[row+1]]
        neighbors = set()
        for col in cols:
            neighbors.update(h.indices[h.indptr[col]:h.indptr[col+1]])
        two_step.append(len(neighbors))
    f = dict(volume=case.blocks*case.rounds, distance=case.distance,
             n_detectors=h.shape[0], n_faults=h.shape[1], nnz=h.nnz,
             prior_sum=float(priors.sum()), expected_activity=float(expected.sum()),
             row_degree_var=float(rd.var()), col_degree_var=float(cd.var()),
             row_degree_p95=float(np.quantile(rd, .95)), col_degree_p95=float(np.quantile(cd, .95)),
             hyperedge_fraction=float(np.mean(cd > 2)), max_arity=int(cd.max()),
             components=int(active.sum()), largest_component_fraction=float(detector_counts.max()/h.shape[0]),
             component_size_second_moment=float(np.sum((detector_counts[active]/h.shape[0])**2)),
             two_step_mean=float(np.mean(two_step)),
             largest_bipartite_component=int(counts.max()))
    f["feature_time_ns"] = time.perf_counter_ns()-t0
    return f


def make_decoder(h, priors, *, stats=False):
    d = BpLsdDecoder(h, error_channel=priors, **DECODER_CONFIG)
    d.set_do_stats(stats)
    return d


def source_manifest():
    return {str(p.relative_to(SOURCE)): digest(p.read_bytes())
            for p in sorted(SOURCE.rglob("*"))
            if p.is_file() and not any(x.startswith(".") or x == "__pycache__" for x in p.relative_to(SOURCE).parts)}


def prepare():
    records = []
    for case in cases():
        t0 = time.perf_counter_ns()
        c = build(case)
        build_ns = time.perf_counter_ns()-t0
        t0 = time.perf_counter_ns()
        dem = c.detector_error_model(decompose_errors=False)
        dem_ns = time.perf_counter_ns()-t0
        t0 = time.perf_counter_ns()
        h, l, p, _ = convert(dem)
        convert_ns = time.perf_counter_ns()-t0
        ctext, dtext = str(c), str(dem)
        (ROOT/"circuits"/f"{case.name}.stim").write_text(ctext)
        (ROOT/"circuits"/f"{case.name}.dem").write_text(dtext)
        np.savez_compressed(ROOT/"circuits"/f"{case.name}.npz", h_data=h.data, h_indices=h.indices,
                            h_indptr=h.indptr, h_shape=h.shape, l_data=l.data, l_indices=l.indices,
                            l_indptr=l.indptr, l_shape=l.shape, priors=p)
        records.append(dict(name=case.name, case=asdict(case), gates=case.gates,
                            event_rounds=case.event_rounds, circuit_sha256=digest(ctext.encode()),
                            dem_sha256=digest(dtext.encode()), features=features(case,h,l,p),
                            circuit_build_ns=build_ns, dem_build_ns=dem_ns, convert_ns=convert_ns))
    environment = dict(python=sys.version, executable=sys.executable, machine=platform.machine(),
                       platform=platform.platform(), processor=platform.processor(),
                       packages={n:importlib.metadata.version(n) for n in ("numpy","scipy","stim","ldpc","sinter","scikit-learn")},
                       threads={k:os.environ[k] for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS")})
    (ROOT/"requirements.lock.txt").write_text(subprocess.check_output([sys.executable,"-m","pip","freeze"], text=True))
    save_json(ROOT/"corpus.json", records)
    save_json(ROOT/"environment.json",environment)
    save_json(ROOT/"source_manifest.json",dict(repository="https://github.com/basilthebeagles/tmcbs", commit=COMMIT,
              archive_sha256=digest((ROOT/"sources"/"tmcbs-c0490fa.tar.gz").read_bytes()), files=source_manifest()))
    print(json.dumps(dict(cases=len(records), sizes=sorted(set(r["features"]["n_detectors"] for r in records)))))


def check_converter():
    dem = stim.DetectorErrorModel("""error(0.1) D0 L0
error(0.2) D0 L0
error(0.15) D0 ^ D0 D1
error(0.03) L1
error(0.04) D0 L1
repeat 2 {
  error(0.05) D0
  shift_detectors 1
}
detector D2
""")
    h,l,p,m = convert(dem)
    assert np.isclose(p[0],.26)
    assert h[0,1] == 0 and h[1,1] == 1
    assert l[1,2] == 1 and h[:,2].nnz == 0
    assert m[0] == m[1] and m[0] != m[4]
    reconstruct(dem, 1000, "synthetic")
    # Correlated separator components must remain one event, not independent.
    d2=stim.DetectorErrorModel("error(0.1) D0 ^ D1")
    h2,l2,p2,m2=convert(d2)
    assert h2.shape==(2,1) and h2.nnz==2 and p2.shape==(1,)
    return True


def reconstruct(dem, shots, name):
    h,l,p,mapping=convert(dem)
    det,obs,errors=dem.compile_sampler(seed=seed("validation_dem", name)).sample(shots, return_errors=True)
    assert errors.shape[1]==len(mapping)
    canonical=np.zeros((shots,h.shape[1]),dtype=np.uint8)
    for j,col in enumerate(mapping):
        if col>=0:
            canonical[:,col]^=errors[:,j]
    assert np.array_equal((h@canonical.T).T%2,det),name
    assert np.array_equal((l@canonical.T).T%2,obs),name


def validate():
    report={"synthetic_converter":check_converter(),"corpus":[],"truth_tables":[],"codes":[]}
    for d in (3,5,7):
        code=tmcbs.surface_code(d)
        assert not (code.css.hx@code.css.hz.T%2).any()
        assert np.array_equal(code.css.lx@code.css.lz.T%2, np.eye(1))
        report["codes"].append(dict(distance=d,css_commutation=True,logical_pairing=True))
    for record in json.loads((ROOT/"corpus.json").read_text()):
        case=Case(**record["case"])
        c=stim.Circuit((ROOT/"circuits"/f"{case.name}.stim").read_text())
        dem=c.detector_error_model()
        assert not c.without_noise().compile_detector_sampler(seed=seed("ideal",case.name)).sample(128,append_observables=True).any()
        reconstruct(dem,256,case.name)
        h,l,p,_=convert(dem)
        hu,lu,pu=tmcbs.parity_check_matrices(c)
        assert np.array_equal(h.toarray(),hu.toarray()) and np.array_equal(l.toarray(),lu.toarray())
        prior_diff=float(np.max(np.abs(p-pu)))
        diag=dict(name=case.name,ideal=True,dem_reconstruction=True,upstream_prior_max_difference=prior_diff)
        if case.distance==3 and case.placement in ("none","spread"):
            n=20000
            dc,oc=c.compile_detector_sampler(seed=seed("circuit_marginals",case.name)).sample(n,separate_observables=True)
            dd,od,_=dem.compile_sampler(seed=seed("dem_marginals",case.name)).sample(n)
            ac=np.concatenate((dc.mean(axis=0),oc.mean(axis=0)))
            ad=np.concatenate((dd.mean(axis=0),od.mean(axis=0)))
            pooled=(ac+ad)/2
            tolerances=6*np.sqrt(2*pooled*(1-pooled)/n)+6/n
            assert np.all(np.abs(ac-ad)<=tolerances),case.name
            diag["circuit_dem_marginal_check"]=True
            diag["max_marginal_difference"]=float(np.max(np.abs(ac-ad)))
        report["corpus"].append(diag)
    # Independent raw logical-Z truth tables: test each complete computational
    # basis, rather than using observables relative to Stim's reference sample.
    for q,programs in PROGRAMS.items():
        for family,gates in programs.items():
            case=Case(3,q,family,"spread" if gates else "none")
            code=tmcbs.surface_code(3)
            for number in range(1<<q):
                bits=np.array([(number>>j)&1 for j in range(q)],dtype=np.uint8)
                expected=bits.copy()
                for a,b in gates:
                    expected[b]^=expected[a]
                c=build(case,input_bits=bits,noise=0)
                assert not c.compile_detector_sampler(seed=1).sample(32).any()
                measurements=c.compile_sampler(seed=2).sample(32).astype(np.uint8)
                data=measurements[:,-q*code.n:].reshape(32,q,code.n)
                observed=(data@code.css.lz.T)[:,:,0]%2
                assert np.all(observed==expected[None,:]),(case.name,bits,observed)
            report["truth_tables"].append(dict(blocks=q,family=family,inputs=1<<q,passed=True))
    save_json(ROOT/"validation.json",report)
    print(json.dumps(dict(validated_circuits=len(report["corpus"]),truth_tables=len(report["truth_tables"]),
                         max_upstream_prior_difference=max(r["upstream_prior_max_difference"] for r in report["corpus"]))))


def freeze():
    assert (ROOT/"validation.json").exists()
    config=dict(sessions=3,shots=2000,warmup=32,decoder=DECODER_CONFIG,commit=COMMIT,
                scope="TMCBS logical-Z detector sector; full-block windows",
                protocol_sha256=digest((ROOT/"PROTOCOL.md").read_bytes()),
                corpus_sha256=digest((ROOT/"corpus.json").read_bytes()),
                analysis_sha256=digest((ROOT/"analyze.py").read_bytes()),
                source_manifest_sha256=digest((ROOT/"source_manifest.json").read_bytes()),
                implementation_sha256=digest(Path(__file__).read_bytes()))
    if (ROOT/"frozen_config.json").exists():
        assert json.loads((ROOT/"frozen_config.json").read_text())==config,"Frozen configuration changed"
    save_json(ROOT/"frozen_config.json",config)
    print(digest((ROOT/"frozen_config.json").read_bytes()))


def benchmark_one(record, session, cfg, *, calibration=False):
    case=Case(**record["case"])
    ctext=(ROOT/"circuits"/f"{case.name}.stim").read_text()
    assert digest(ctext.encode())==record["circuit_sha256"]
    c=stim.Circuit(ctext)
    h,l,priors,_=convert(c.detector_error_model())
    t0=time.perf_counter_ns()
    decoder=make_decoder(h,priors)
    init_ns=time.perf_counter_ns()-t0
    prefix="calibration" if calibration else "timing"
    warm=c.compile_detector_sampler(seed=seed(prefix+"_warm",session,case.name)).sample(cfg["warmup"]).astype(np.uint8)
    for s in warm:
        decoder.decode(s)
    t0=time.perf_counter_ns()
    det,obs=c.compile_detector_sampler(seed=seed(prefix+"_shots",session,case.name)).sample(cfg["shots"],separate_observables=True)
    det=det.astype(np.uint8)
    sampling_ns=time.perf_counter_ns()-t0
    n=len(det)
    latency=np.zeros(n,dtype=np.int64)
    iterations=np.zeros(n,dtype=np.int32)
    converge=np.zeros(n,dtype=bool)
    corrections=np.zeros((n,h.shape[1]),dtype=np.uint8)
    loop0=time.perf_counter_ns()
    for j,s in enumerate(det):
        t0=time.perf_counter_ns()
        correction=decoder.decode(s)
        latency[j]=time.perf_counter_ns()-t0
        corrections[j]=correction
        iterations[j]=decoder.iter
        converge[j]=decoder.converge
    loop_ns=time.perf_counter_ns()-loop0
    invalid=np.any((h@corrections.T).T%2 !=det,axis=1)
    mismatches=np.any((l@corrections.T).T%2 !=obs,axis=1)
    if invalid.any():
        raise AssertionError(f"Invalid corrections: {case.name}: {invalid.sum()}")
    dest=ROOT/"results"/("calibration" if calibration else f"session_{session}")
    dest.mkdir(parents=True,exist_ok=True)
    checkpoints=np.unique(np.concatenate((np.arange(min(16,n)),np.argsort(latency)[-16:])))
    np.savez_compressed(dest/f"{case.name}.npz",latency_ns=latency,bp_iterations=iterations,
                        bp_converged=converge,logical_z_failure=mismatches,
                        syndrome_weight=det.sum(axis=1),invalid_correction=invalid,
                        checkpoint_indices=checkpoints,checkpoint_detectors=det[checkpoints],
                        checkpoint_observables=obs[checkpoints],checkpoint_corrections=corrections[checkpoints])
    summary=dict(name=case.name,session=session,shots=n,seed=seed(prefix+"_shots",session,case.name),
                 mean_ns=float(latency.mean()),median_ns=float(np.median(latency)),
                 p95_ns=float(np.quantile(latency,.95)),p99_ns=float(np.quantile(latency,.99)),
                 logical_z_failures=int(mismatches.sum()),invalid_corrections=int(invalid.sum()),
                 bp_fallback_fraction=float(np.mean(~converge)),bp_iterations_mean=float(iterations.mean()),
                 zero_syndrome_fraction=float(np.mean(det.sum(axis=1)==0)),
                 decoder_init_ns=init_ns,sampling_ns=sampling_ns,decode_loop_wall_ns=loop_ns,
                 config_sha256=digest((ROOT/"frozen_config.json").read_bytes()),
                 implementation_sha256=digest(Path(__file__).read_bytes()))
    save_json(dest/f"{case.name}.json",summary)
    return summary


def run(*,calibration=False):
    cfg=json.loads((ROOT/"frozen_config.json").read_text())
    assert digest((ROOT/"PROTOCOL.md").read_bytes())==cfg["protocol_sha256"]
    assert digest((ROOT/"corpus.json").read_bytes())==cfg["corpus_sha256"]
    assert digest(Path(__file__).read_bytes())==cfg["implementation_sha256"]
    records=json.loads((ROOT/"corpus.json").read_text())
    if calibration:
        cfg={**cfg,"shots":128}
        records=[r for r in records if r["name"] in ("d3_q2_single_spread","d7_q4_fanout_spread")]
    for session in range(1 if calibration else cfg["sessions"]):
        ordered=list(records)
        np.random.default_rng(seed("case_order",session)).shuffle(ordered)
        for index,record in enumerate(ordered):
            dest=ROOT/"results"/("calibration" if calibration else f"session_{session}")/f"{record['name']}.json"
            if dest.exists():
                print(json.dumps(dict(skipped=record["name"],session=session)),flush=True)
                continue
            summary=benchmark_one(record,session,cfg,calibration=calibration)
            print(json.dumps({k:summary[k] for k in ("name","session","mean_ns","p95_ns","logical_z_failures")}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["prepare","validate","freeze","calibrate","run"])
    args=parser.parse_args()
    if args.action=="prepare": prepare()
    elif args.action=="validate": validate()
    elif args.action=="freeze": freeze()
    elif args.action=="calibrate": run(calibration=True)
    elif args.action=="run": run()
