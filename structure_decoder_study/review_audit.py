"""Second-pass numerical review without importing the fitting/measurement code.

Read-only for existing artifacts. New outputs go to review/. The closed-form
ridge calculation provides an implementation separate from sklearn's pipeline.
"""
from __future__ import annotations
from collections import defaultdict
import csv,hashlib,json
from pathlib import Path
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent
FEATURES={
    "B0_volume":["volume","distance"],
    "B1_dimensions":["distance","n_detectors","n_faults"],
    "B2_sparsity_activity":["distance","n_detectors","n_faults","nnz","prior_sum","expected_activity"],
    "B3_structure":["distance","n_detectors","n_faults","nnz","prior_sum","expected_activity",
                    "row_degree_var","col_degree_var","row_degree_p95","col_degree_p95",
                    "hyperedge_fraction","components","largest_component_fraction",
                    "component_size_second_moment","two_step_mean"],
}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def quantile_linear(values,q):
    v=np.sort(values)
    position=q*(len(v)-1)
    lo=int(np.floor(position));hi=int(np.ceil(position))
    fraction=position-lo
    return float(v[lo]*(1-fraction)+v[hi]*fraction)


def ridge_oof(x,y,groups):
    result=np.full(len(y),np.nan)
    for group in sorted(set(groups)):
        test=groups==group;train=~test
        center=x[train].mean(axis=0)
        scale=x[train].std(axis=0)
        scale[scale<1e-14]=1
        design=(x[train]-center)/scale
        yy=np.log(y[train]);intercept=yy.mean()
        beta=np.linalg.solve(design.T@design+np.eye(x.shape[1]),design.T@(yy-intercept))
        result[test]=np.exp(intercept+((x[test]-center)/scale)@beta)
    return result


def score(pred,y,groups):
    errors=np.abs(np.log(pred/y))
    return float(np.exp(np.mean([errors[groups==g].mean() for g in sorted(set(groups))])))


def components_by_union_find(h):
    parent=list(range(h.shape[0]))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for j in range(h.shape[1]):
        rows=h.indices[h.indptr[j]:h.indptr[j+1]]
        if len(rows)>1:
            first=find(int(rows[0]))
            for row in rows[1:]:parent[find(int(row))]=first
    return len({find(i) for i in range(h.shape[0])})


def main():
    manifest=json.loads((ROOT/"artifact_manifest.json").read_text())
    mismatches=[name for name,expected in manifest["files"].items()
                if not (ROOT/name).exists() or sha(ROOT/name)!=expected]
    assert not mismatches,mismatches
    records=json.loads((ROOT/"corpus.json").read_text())
    recorded=json.loads((ROOT/"results/analysis.json").read_text())
    predictions=list(csv.DictReader((ROOT/"results/predictions.csv").open()))
    raw_summaries=[]
    max_activity_difference=0.
    shots=0;invalid=0;failures=0
    for record in records:
        name=record["name"]
        matrices=np.load(ROOT/"circuits"/f"{name}.npz")
        h=sp.csc_matrix((matrices["h_data"],matrices["h_indices"],matrices["h_indptr"]),shape=tuple(matrices["h_shape"]))
        priors=matrices["priors"]
        f=record["features"]
        assert h.shape==(f["n_detectors"],f["n_faults"])
        assert h.nnz==f["nnz"]
        assert np.all((priors>=0)&(priors<.5))
        expected=float(np.sum(-.5*np.expm1(h@np.log1p(-2*priors))))
        max_activity_difference=max(max_activity_difference,abs(expected-f["expected_activity"]))
        assert abs(expected-f["expected_activity"])<1e-9
        assert abs(priors.sum()-f["prior_sum"])<1e-9
        assert components_by_union_find(h)==f["components"]
        samples=[]
        for session in range(3):
            data=np.load(ROOT/"results"/f"session_{session}"/f"{name}.npz")
            samples.append(data["latency_ns"])
            shots+=len(data["latency_ns"])
            invalid+=int(data["invalid_correction"].sum())
            failures+=int(data["logical_z_failure"].sum())
        times=np.concatenate(samples)
        raw_summaries.append(dict(name=name,mean_ns=int(times.sum())/len(times),p95_ns=quantile_linear(times,.95)))
    assert shots==468000 and invalid==0 and failures==recorded["logical_z_failures"]
    groups=np.array([r["case"]["family"] for r in records])
    connected=np.array([r["features"]["components"]==1 for r in records])
    report=dict(artifact_files_checked=len(manifest["files"]),hash_mismatches=mismatches,
                shots=shots,invalid_correction_flags=invalid,logical_z_failure_flags=failures,
                max_expected_activity_difference=max_activity_difference,
                primary_metrics={},connected_metrics={},semantic_group_sensitivity={},
                max_relative_prediction_difference=0.,external_peer_review=False)
    for target in ("mean_ns","p95_ns"):
        y=np.array([r[target] for r in raw_summaries])
        report["primary_metrics"][target]={};report["connected_metrics"][target]={}
        report["semantic_group_sensitivity"][target]={}
        saved={r["name"]:r for r in predictions if r["target"]==target}
        for model,columns in FEATURES.items():
            x=np.log1p([[r["features"][c] for c in columns] for r in records])
            pred=ridge_oof(x,y,groups)
            expected=np.array([float(saved[r["name"]][model]) for r in records])
            discrepancy=float(np.max(np.abs(pred/expected-1)))
            report["max_relative_prediction_difference"]=max(report["max_relative_prediction_difference"],discrepancy)
            assert discrepancy<1e-7,(target,model,discrepancy)
            metric=score(pred,y,groups)
            assert np.isclose(metric,recorded["metrics"][target][model]["family_balanced_multiplicative_error"])
            report["primary_metrics"][target][model]=metric
            cmetric=score(ridge_oof(x[connected],y[connected],groups[connected]),y[connected],groups[connected])
            assert np.isclose(cmetric,recorded["connected_metrics"][target][model]["family_balanced_multiplicative_error"])
            report["connected_metrics"][target][model]=cmetric
            # Single CNOT and three identical CNOTs implement the same ideal
            # logical map. Merge the labels conservatively across both sizes.
            merged=np.array(["single_or_repeated" if g in ("single","repeated") else g for g in groups])
            report["semantic_group_sensitivity"][target][model]=score(ridge_oof(x,y,merged),y,merged)
    maps=defaultdict(list)
    seen=set()
    for record in records:
        q=record["case"]["blocks"];family=record["case"]["family"]
        if (q,family) in seen:continue
        seen.add((q,family))
        matrix=np.eye(q,dtype=np.uint8)
        for a,b in record["gates"]:matrix[b]^=matrix[a]
        maps[(q,tuple(matrix.flat))].append(family)
    report["logical_map_aliases"]=[dict(blocks=k[0],families=v) for k,v in maps.items() if len(v)>1]
    # The sampled two-step descriptor uses selected detector IDs and therefore
    # need not be invariant under a row permutation. Recompute on 20 relabelings.
    record=next(r for r in records if r["name"]=="d7_q4_cycle_late")
    m=np.load(ROOT/"circuits"/f"{record['name']}.npz")
    h=sp.csc_matrix((m["h_data"],m["h_indices"],m["h_indptr"]),shape=tuple(m["h_shape"]))
    def two_step(matrix):
        csr=matrix.tocsr();values=[]
        for row in np.unique(np.linspace(0,matrix.shape[0]-1,min(32,matrix.shape[0]),dtype=int)):
            neighbors=set()
            for col in csr.indices[csr.indptr[row]:csr.indptr[row+1]]:
                neighbors.update(matrix.indices[matrix.indptr[col]:matrix.indptr[col+1]])
            values.append(len(neighbors))
        return float(np.mean(values))
    rng=np.random.default_rng(20261112)
    values=[two_step(h[rng.permutation(h.shape[0]),:].tocsc()) for _ in range(20)]
    report["two_step_relabeling_diagnostic"]=dict(case=record["name"],original=two_step(h),
                    randomized_min=min(values),randomized_max=max(values),permutations=20,
                    note="Feature approximation depends on selected row IDs; decoder timings are not rerun")
    output=ROOT/"review";output.mkdir(exist_ok=True)
    (output/"numerical_review.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
