"""Post hoc nested regularization control. See ROBUSTNESS_PROTOCOL.md."""
from __future__ import annotations
import json
import os
from pathlib import Path
for n in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[n]="1"
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from analyze_v2 import MODELS,score

ROOT=Path(__file__).resolve().parent
ALPHAS=[.01,.1,1.,10.,100.]
B2=MODELS["B2_sparsity_activity"]
SETS={"B2_tuned":B2,
      "B3_local_tuned":B2+["row_degree_var","col_degree_var","row_degree_p95","col_degree_p95","hyperedge_fraction"],
      "B3_components_tuned":B2+["components","largest_component_fraction","component_size_second_moment"],
      "B3_full_tuned":MODELS["B3_structure"]}


def fit_predict(x,y,train,test,alpha):
    model=make_pipeline(StandardScaler(),Ridge(alpha=alpha))
    model.fit(x[train],np.log(y[train]))
    return model.predict(x[test])


def evaluate(records,summary):
    groups=np.array([r["case"]["family"] for r in records])
    result={}
    for target in ("mean_ns","p95_ns"):
        yy=np.array([r[target] for r in summary])
        result[target]={}
        for name,columns in SETS.items():
            x=np.log1p([[r["features"][c] for c in columns] for r in records])
            prediction=np.full(len(yy),np.nan)
            selections={}
            for held_family in sorted(set(groups)):
                test=groups==held_family
                outer=~test
                inner_groups=sorted(set(groups[outer]))
                losses=[]
                for alpha in ALPHAS:
                    family_losses=[]
                    for inner in inner_groups:
                        validation=groups==inner
                        training=outer&~validation
                        predlog=fit_predict(x,yy,training,validation,alpha)
                        family_losses.append(float(np.mean(np.abs(predlog-np.log(yy[validation])))))
                    losses.append(float(np.mean(family_losses)))
                chosen=ALPHAS[int(np.argmin(losses))]
                selections[held_family]=dict(alpha=chosen,inner_losses=dict(zip(map(str,ALPHAS),losses)))
                prediction[test]=np.exp(fit_predict(x,yy,outer,test,chosen))
            result[target][name]=dict(**score(prediction,yy,groups),selections=selections,
                                      predictions_ns=prediction.tolist())
    return result


def main():
    records=json.loads((ROOT/"corpus.json").read_text())
    summaries=json.loads((ROOT/"results"/"case_summaries.json").read_text())
    connected=[r["features"]["components"]==1 for r in records]
    result=dict(post_hoc=True,alpha_grid=ALPHAS,
                full=evaluate(records,summaries),
                connected=evaluate([r for r,k in zip(records,connected) if k],
                                   [r for r,k in zip(summaries,connected) if k]))
    (ROOT/"results"/"robustness.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({part:{target:{model:round(v["family_balanced_multiplicative_error"],4)
                                   for model,v in models.items()}
                           for target,models in result[part].items()}
                      for part in ("full","connected")}))


if __name__=="__main__":main()
