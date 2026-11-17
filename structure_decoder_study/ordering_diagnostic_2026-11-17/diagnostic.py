"""Implementation-derived ordering diagnostic; no decoder/candidate searches."""
from pathlib import Path
import ctypes as C
import hashlib,json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
OLD=STUDY/"natural_noise_reproduction_2026-11-17"
HEAD=STUDY/"headroom_1fv_2026-11-17"
SOURCE=OLD/"sources/Adaptive-qLDPC-8cc3201"
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[name]="1"
sys.dont_write_bytecode=True


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")


def prepare():
    assert not (ROOT/"frozen.json").exists()
    for name,digest in read(HEAD/"manifest.json")["files"].items():assert sha(HEAD/name)==digest,name
    so=Path('.venv/lib/python3.12/site-packages/ldpc/bposd_decoder/_bposd_decoder.cpython-312-darwin.so').resolve()
    paths=[ROOT/"PROTOCOL.md",Path(__file__),ROOT/"source_manifest.json",ROOT/"reference_manifest.json",ROOT/"installed_sort_disassembly.txt",
        HEAD/"selection.json",OLD/"entry/H.npz",SOURCE/"failure_prediction/osd_internals.py",SOURCE/"failure_prediction/__init__.py",so]
    for row in read(HEAD/"selection.json"):paths+=[Path(row["cached_npz"]),Path(row["cached_metadata"])]
    frozen=dict(files={str(p.resolve()):sha(p) for p in paths},binary=str(so),selection=read(HEAD/"selection.json"),
        ordering_rule="Exact installed comparator plus platform qsort, ascending initial indices",wall_timeout_seconds=120,new_native_decoder_calls=0,new_physical_shots=0)
    save(ROOT/"frozen.json",frozen)
    print(json.dumps(dict(frozen=True,cases=24,files_hashed=len(paths))))


def worker():
    import numpy as np
    import scipy.sparse as sp
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    sys.path.insert(0,str(SOURCE))
    from failure_prediction.osd_internals import pack_matrix,osd0_information_set
    class Item(C.Structure):_fields_=[("value",C.c_double),("index",C.c_int)]
    assert C.sizeof(Item)==16 and C.alignment(Item)==8 and Item.value.offset==0 and Item.index.offset==8
    lib=C.CDLL(frozen["binary"])
    cmp=getattr(lib,"_ZN4ldpc4sort3cmpEPKvS2_")
    cmp.argtypes=[C.c_void_p,C.c_void_p];cmp.restype=C.c_int
    qsort=C.CDLL(None).qsort
    qsort.argtypes=[C.c_void_p,C.c_size_t,C.c_size_t,C.c_void_p];qsort.restype=None
    def native_order(values):
        assert np.isfinite(values).all()
        array=(Item*len(values))()
        for i,value in enumerate(values):array[i].value=float(value);array[i].index=i
        qsort(array,len(values),C.sizeof(Item),C.cast(cmp,C.c_void_p))
        result=np.array([x.index for x in array],dtype=np.int64)
        assert np.array_equal(np.sort(result),np.arange(len(values)))
        assert np.all(np.diff(values[result])>=0)
        return result
    a,b=Item(1.25,0),Item(1.25,999)
    assert cmp(C.byref(a),C.byref(b))==0
    b.value=2.;assert cmp(C.byref(a),C.byref(b))<0
    b.value=-2.;assert cmp(C.byref(a),C.byref(b))>0
    for values in (np.array([2.,1.,1.,-1.]),np.zeros(100),np.arange(100.)[::-1]):
        assert np.array_equal(native_order(values),native_order(values))
    h=sp.load_npz(OLD/"entry/H.npz").tocsr();packed=pack_matrix(h,12240,1)
    def rank(matrix):
        x=matrix.tocsr();basis={}
        for i in range(x.shape[0]):
            word=sum(1<<int(j) for j in x.indices[x.indptr[i]:x.indptr[i+1]])
            while word:
                pivot=word.bit_length()-1
                if pivot in basis:word^=basis[pivot]
                else:basis[pivot]=word;break
        return len(basis)
    out=ROOT/"cases";out.mkdir()
    rows=[];started=time.perf_counter()
    for case in frozen["selection"]:
        cid=case["case_id"];data=np.load(case["cached_npz"])
        llr,syndrome,reference=data["llrs"].copy(),data["syndrome"].copy(),data["correction"].copy()
        order=native_order(llr);assert np.array_equal(order,native_order(llr))
        priority=np.empty(12240,dtype=np.float64);priority[order]=np.arange(12240,dtype=np.float64)
        stable=osd0_information_set(packed,syndrome,llr,12240,1794)
        adapted=osd0_information_set(packed,syndrome,priority,12240,1794)
        assert stable is not None and adapted is not None
        assert np.array_equal(adapted["order"],order)
        for info in (stable,adapted):
            assert np.array_equal(h@info["solution"]%2,syndrome)
            assert rank(h[:,info["pivot_cols"]])==1794
            mask=np.zeros(12240,dtype=bool);mask[info["pivot_cols"]]=True
            assert not info["solution"][~mask].any()
        row=dict(case_id=cid,stable_difference=int(np.count_nonzero(stable["solution"]!=reference)),
            native_order_difference=int(np.count_nonzero(adapted["solution"]!=reference)),
            ordering_positions_changed=int(np.count_nonzero(stable["order"]!=order)))
        np.savez_compressed(out/f"{cid:04d}.npz",native_order=order,stable_order=stable["order"],
            stable_solution=stable["solution"],native_order_solution=adapted["solution"],stable_pivots=stable["pivot_cols"],native_order_pivots=adapted["pivot_cols"])
        save(out/f"{cid:04d}.json",row);rows.append(row)
    result=dict(status="completed",cases=len(rows),rows=rows,stable_exact_matches=sum(x["stable_difference"]==0 for x in rows),
        native_order_exact_matches=sum(x["native_order_difference"]==0 for x in rows),
        native_order_repeatable=True,abi_adapters_passed=True,native_decoder_calls=0,physical_shots=0,candidate_searches=0,
        elapsed_seconds=time.perf_counter()-started,frozen_sha256=sha(ROOT/"frozen.json"),
        scope="Implementation-derived ordering diagnostic on inspected cached panel; not hidden-pivot equivalence or a 1FV experiment")
    save(ROOT/"result.json",result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}))


def run():
    assert not (ROOT/"process_result.json").exists()
    try:
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),"worker"],capture_output=True,text=True,timeout=120)
        record=dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
    except subprocess.TimeoutExpired as exc:record=dict(status="timeout",stdout=str(exc.stdout),stderr=str(exc.stderr))
    save(ROOT/"process_result.json",record)
    print(json.dumps(record))


if __name__=="__main__":
    assert len(sys.argv)==2 and sys.argv[1] in ("prepare","run","worker")
    {"prepare":prepare,"run":run,"worker":worker}[sys.argv[1]]()
