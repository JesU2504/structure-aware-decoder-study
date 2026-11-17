"""Prespecified pre-confirmation fixed-prefix risk diagnostic."""
from pathlib import Path
import json
import numpy as np
from analyze import probability_interval
ROOT=Path(__file__).resolve().parent

def main():
    names=json.loads((ROOT/"confirmation_selection.json").read_text())["names"]
    records={r["name"]:r for r in json.loads((ROOT/"corpus.json").read_text())}
    result=[]
    for name in names:
        row=dict(name=name,prefix_per_session=256,secondary=True,complete=True)
        times=[];failures=[];sessions=[]
        for session in range(3):
            a=np.load(ROOT/"results/confirmation"/f"session_{session}"/f"{name}.npz")
            if len(a["wall_ns"])<256:row["complete"]=False;break
            t=a["wall_ns"][:256];times.append(t);failures.extend(a["logical_z_failure"][:256])
            misses=int(np.sum(t>records[name]["budget_ns"]))
            sessions.append(dict(session=session,misses=misses,miss_probability=misses/256,
                                 interval=probability_interval(misses,256,.05/(len(names)*3))))
        if row["complete"]:
            t=np.concatenate(times);misses=int(np.sum(t>records[name]["budget_ns"]))
            bounds=probability_interval(misses,len(t),.05/len(names))
            admitted=records[name]["predictions"]["p95_ns"]["B2"]["padded_ns"]<=records[name]["budget_ns"]
            row.update(shots=len(t),miss_probability=misses/len(t),miss_interval=bounds,
                       logical_z_failures=int(np.sum(failures)),logical_z_failure_fraction=float(np.mean(failures)),
                       padded_admitted=admitted,confident_false_admission=(admitted and bounds[0]>.05),
                       all_sessions_false_admission=(admitted and all(s["interval"][0]>.05 for s in sessions)),
                       session_intervals=sessions)
        result.append(row)
    (ROOT/"results/confirmation_prefix.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
