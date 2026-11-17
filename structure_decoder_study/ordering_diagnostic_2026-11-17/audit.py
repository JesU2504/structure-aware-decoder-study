"""Independent saved ordering/baseline audit; no reconstruction/decoder calls."""
from pathlib import Path
import hashlib,json
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
OLD=STUDY/"natural_noise_reproduction_2026-11-17"
HEAD=STUDY/"headroom_1fv_2026-11-17"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())


def rank(matrix):
    a=matrix.tocsr();basis={}
    for i in range(a.shape[0]):
        word=sum(1<<int(j) for j in a.indices[a.indptr[i]:a.indptr[i+1]])
        while word:
            p=word.bit_length()-1
            if p in basis:word^=basis[p]
            else:basis[p]=word;break
    return len(basis)


def main():
    f=read(ROOT/"frozen.json");result=read(ROOT/"result.json")
    for name,digest in f["files"].items():assert sha(Path(name))==digest,name
    assert result["status"]=="completed" and read(ROOT/"process_result.json")["returncode"]==0
    assert result["frozen_sha256"]==sha(ROOT/"frozen.json")
    h=sp.load_npz(OLD/"entry/H.npz").tocsr()
    stable_count=native_count=0
    for case,row in zip(f["selection"],result["rows"]):
        cid=case["case_id"];assert row["case_id"]==cid
        cached=np.load(case["cached_npz"]);data=np.load(ROOT/"cases"/f"{cid:04d}.npz")
        llr=cached["llrs"];reference=cached["correction"]
        assert np.array_equal(data["stable_order"],np.asarray(sorted(range(12240),key=lambda i:(llr[i],i))))
        assert np.array_equal(np.sort(data["native_order"]),np.arange(12240))
        assert np.array_equal(llr[data["stable_order"]],llr[data["native_order"]]),"Ordering must differ only inside exact ties"
        for prefix in ("stable","native_order"):
            solution=data[prefix+"_solution"];pivot=data[prefix+"_pivots"]
            assert rank(h[:,pivot])==1794
            assert np.array_equal(h@solution%2,cached["syndrome"])
            mask=np.zeros(12240,dtype=bool);mask[pivot]=True
            assert not solution[~mask].any()
        stable_diff=int(np.count_nonzero(data["stable_solution"]!=reference))
        native_diff=int(np.count_nonzero(data["native_order_solution"]!=reference))
        assert stable_diff==row["stable_difference"] and native_diff==row["native_order_difference"]
        stable_count+=stable_diff==0;native_count+=native_diff==0
    assert stable_count==23 and native_count==24
    assert [r["case_id"] for r in result["rows"] if r["stable_difference"]]>[]
    assert [r["case_id"] for r in result["rows"] if r["stable_difference"]]==[51]
    preserved={}
    previous=list(read(HEAD/"result_audit.json")["previous_manifests_verified"])+["headroom_1fv_2026-11-17/manifest.json"]
    for name in previous:
        p=STUDY/name;files=read(p)["files"]
        for relative,digest in files.items():assert sha(p.parent/relative)==digest,(name,relative)
        preserved[name]=len(files)
    report=dict(passed=True,cases=24,stable_matches=23,native_sort_equivalent_matches=24,
        changes_only_within_exact_reliability_ties=True,all1800_syndrome_equations_pass=True,all_pivot_ranks=1794,
        native_decoder_calls=0,physical_shots=0,candidate_searches=0,previous_manifests_verified=preserved,
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)),
        interpretation="Implementation-derived sorting accounts for the observed mismatch on this panel; original stable-branch experiment remains stopped, no hidden native pivot or across-platform equivalence claimed")
    (ROOT/"audit.json").write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='previous_manifests_verified'}))


if __name__=="__main__":main()
