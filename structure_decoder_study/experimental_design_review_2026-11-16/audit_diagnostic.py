"""Independent checks of saved diagnostic choices/splits/metrics and history."""
from pathlib import Path
import hashlib
import json
import math
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    cfg=read(ROOT/"grid_config.json")
    for relative,expected in cfg["inputs"].items():
        assert sha(STUDY/relative)==expected,relative
    result=read(ROOT/"grid_results.json")
    assert result["complete"] and result["numerical_checks"]["passed"]
    assert result["config_sha256"]==sha(ROOT/"grid_config.json")
    rows=read(ROOT/"grid_checkpoints.json")
    assert len(rows)==result["outer_model_evaluations"]==372
    data={r["name"]:r for r in read(STUDY/"learning_curves_2026-11-13/dataset.json")}
    lookup={(r["grid"],r["domain"],r["held"],r["model"]):r for r in rows}
    maximum_subset_loss_difference=0.
    for r in rows:
        train,test=set(r["train_names"]),set(r["test_names"])
        assert train and test and not train & test
        assert not {data[n]["group"] for n in train} & {data[n]["group"] for n in test}
        assert all(data[n]["group"]==r["held"] for n in test)
        losses=np.array(r["inner_losses"])
        assert len(losses)==len(r["candidates"])
        assert np.array_equal(np.array(r["chosen"],dtype=object),
                              np.array([r["candidates"][i] for i in losses.argmin(axis=0)],dtype=object))
        y=np.log([[data[n]["targets"][t] for t in ("mean_ns","p95_ns")] for n in r["test_names"]])
        expected=np.abs(np.array(r["predicted_log"])-y).mean(axis=0)
        assert np.allclose(expected,r["heldout_mae_log"],rtol=1e-12,atol=1e-12)
        if r["grid"]=="extended":
            old=lookup["original",r["domain"],r["held"],r["model"]]
            assert old["train_names"]==r["train_names"] and old["test_names"]==r["test_names"]
            mapping={tuple(c):i for i,c in enumerate(r["candidates"])}
            subset=np.array([losses[mapping[tuple(c)]] for c in old["candidates"]])
            error=float(np.max(np.abs(subset-np.array(old["inner_losses"]))))
            maximum_subset_loss_difference=max(maximum_subset_loss_difference,error)
            assert error<1e-8
            assert np.all(losses.min(axis=0)<=np.array(old["inner_losses"]).min(axis=0)+1e-10)
    for grid,report in result["grids"].items():
        for summary in report["summary"]:
            t=0 if summary["target"]=="mean_ns" else 1
            matching=[r for r in rows if r["grid"]==grid and r["domain"]==summary["domain"] and r["model"]==summary["model"]]
            expected=math.exp(np.mean([r["heldout_mae_log"][t] for r in matching]))
            assert math.isclose(expected,summary["heldout_error_factor"],rel_tol=1e-12)
    fallback=read(ROOT/"feature_fallback.json")
    for name,expected in fallback["sources"].items():
        assert sha(ROOT/name)==expected,name
    for summary in fallback["rows"]:
        t=0 if summary["target"]=="mean_ns" else 1
        errors=[]
        for d in summary["details"]:
            a=lookup[summary["grid"],summary["domain"],d["held"],"rbf_density8"]
            b=lookup[summary["grid"],summary["domain"],d["held"],"rbf_graph16"]
            best=b if min(v[t] for v in b["inner_losses"])<min(v[t] for v in a["inner_losses"]) else a
            assert d["selected"]==best["model"]
            errors.append(best["heldout_mae_log"][t])
        assert math.isclose(math.exp(np.mean(errors)),summary["selector_error_factor"],rel_tol=1e-12)
    previous={}
    paths=["artifact_manifest.json","artifact_manifest_2026-11-13.json","artifact_manifest_2026-11-15.json",
        "artifact_manifest_2026-11-16.json","stress_gate/manifest.json","fit_diagnostic_2026-11-13/manifest.json",
        "learning_curves_2026-11-13/manifest.json","reviewer_perspective_2026-11-13/manifest.json",
        "validation_gate_2026-11-13/manifest.json","supervisor_review_2026-11-16/manifest.json",
        "supervisor_review_2026-11-16/cross_domain_manifest.json","novelty_feasibility_2026-11-16/manifest.json",
        "next_stage_design_2026-11-16/manifest.json","consumer_gate_2026-11-16/manifest.json",
        "research_reorientation_2026-11-16/manifest.json"]
    for relative in paths:
        p=STUDY/relative
        files=read(p)["files"]
        for n,h in files.items():assert sha(p.parent/n)==h,(relative,n)
        previous[relative]=len(files)
    report=dict(passed=True,date="2026-11-16",new_decoder_calls=0,new_physical_samples=0,
        outer_model_evaluations_checked=len(rows),independent_sklearn_target_checks=result["selected_independent_sklearn_target_fits"],
        original_candidate_subset_max_inner_loss_difference=maximum_subset_loss_difference,
        feature_family_selection_checks=len(fallback["rows"]),previous_manifests_verified=previous,
        grid_results_sha256=sha(ROOT/"grid_results.json"),grid_checkpoints_sha256=sha(ROOT/"grid_checkpoints.json"),
        source_sha256=sha(Path(__file__)),note="Internal verification; independent AI supervisor review is partial, not complete.")
    (ROOT/"diagnostic_audit.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
