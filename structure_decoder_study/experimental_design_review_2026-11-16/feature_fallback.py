"""Arithmetic reuse of saved inner/outer outcomes; no fitting."""
from pathlib import Path
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parent
GATE = ROOT.parent / "validation_gate_2026-11-13"


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    fits = read(ROOT/"grid_checkpoints.json")
    grid_results = read(ROOT/"grid_results.json")
    corpus = read(GATE/"corpus.json")
    actual = {r["name"]:r for r in read(GATE/"bridge_analysis.json")["summaries"] if r["setting"] == "whole30"}
    rows, bridge_rows = [], []
    for grid in ("original", "extended"):
        for domain in ("original", "fixed_noise", "mixed_noise"):
            base = {r["held"]:r for r in fits if r["grid"] == grid and r["domain"] == domain and r["model"] == "rbf_density8"}
            graph = {r["held"]:r for r in fits if r["grid"] == grid and r["domain"] == domain and r["model"] == "rbf_graph16"}
            for target_index,target in enumerate(("mean_ns", "p95_ns")):
                details = []
                for held in sorted(base):
                    a,b = base[held],graph[held]
                    assert a["train_names"] == b["train_names"] and a["test_names"] == b["test_names"]
                    la=min(r[target_index] for r in a["inner_losses"])
                    lb=min(r[target_index] for r in b["inner_losses"])
                    chosen = b if lb < la else a
                    details.append(dict(held=held,selected=chosen["model"],inner_base_loss=la,inner_graph_loss=lb,
                        selected_outer_mae_log=chosen["heldout_mae_log"][target_index],
                        base_outer_mae_log=a["heldout_mae_log"][target_index]))
                rows.append(dict(grid=grid,domain=domain,target=target,held_groups=len(details),
                    selected_graph_groups=sum(r["selected"] == "rbf_graph16" for r in details),
                    selector_error_factor=math.exp(statistics.mean(r["selected_outer_mae_log"] for r in details)),
                    base_error_factor=math.exp(statistics.mean(r["base_outer_mae_log"] for r in details)),details=details))
        for t,target in enumerate(("mean_ns", "p95_ns")):
            by_parent={}
            for case in corpus:
                domain="original" if case["parent"].startswith("old/") else "mixed_noise"
                selection=next(r for r in rows if r["grid"] == grid and r["domain"] == domain and r["target"] == target)
                chosen=next(r["selected"] for r in selection["details"] if r["held"] == case["parent"])
                prediction=grid_results["grids"][grid]["bridge_predictions_ns"][case["name"]][chosen][t]
                truth=actual[case["name"]]["mean_wall_ns" if t == 0 else "p95_wall_ns"]
                by_parent.setdefault(case["parent"],[]).append(abs(math.log(prediction/truth)))
            bridge_rows.append(dict(grid=grid,target=target,heldout_parent_error_factor=
                math.exp(statistics.mean(statistics.mean(v) for v in by_parent.values()))))
    result=dict(post_hoc_development_only=True,new_model_fits=0,new_decoder_calls=0,rows=rows,bridge=bridge_rows,
        sources={p.name:sha(p) for p in (ROOT/"FEATURE_FALLBACK_AMENDMENT.md",Path(__file__),ROOT/"grid_checkpoints.json",ROOT/"grid_results.json")})
    (ROOT/"feature_fallback.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(rows=[{k:v for k,v in r.items() if k!="details"} for r in rows],bridge=bridge_rows),indent=2))


if __name__ == "__main__":
    main()
