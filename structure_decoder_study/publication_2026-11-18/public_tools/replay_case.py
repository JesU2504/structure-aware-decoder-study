"""Replay one cached primary case. Does not modify archived experiment files."""
from pathlib import Path
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[key]="1"
import argparse,json
import numpy as np
import scipy.sparse as sp
from ldpc import BpOsdDecoder

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--case",type=int,default=23);args=parser.parse_args()
    assert 0<=args.case<512
    base=ROOT/"structure_decoder_study/natural_noise_reproduction_2026-11-17"
    rows=[json.loads(x) for x in (base/"invocations.jsonl").read_text().splitlines()]
    row=next(r for r in rows if r.get("event")=="complete" and r.get("phase")=="main" and r["case_id"]==args.case and r["config"]["name"]=="osd20")
    data=np.load(base/"calls"/f"{row['index']:04d}.npz")
    h=sp.load_npz(base/"entry/H.npz").tocsr();l=sp.load_npz(base/"entry/L.npz").tocsr();p=np.load(base/"entry/priors.npy")
    decoder=BpOsdDecoder(h,error_channel=p.tolist(),max_iter=20,bp_method="ms",ms_scaling_factor=.625,
                        schedule="parallel",omp_thread_count=1,random_schedule_seed=0,input_vector_type="syndrome",osd_method="OSD_0",osd_order=0)
    correction=decoder.decode(data["syndrome"]).copy()
    result=dict(case=args.case,syndrome_residual=int(np.count_nonzero(h@correction%2!=data["syndrome"])),
        wrong_logical_bits=int(np.count_nonzero(l@correction%2!=data["actual"])),
        exact_saved_correction_match=bool(np.array_equal(correction,data["correction"])),new_decoder_calls=1)
    print(json.dumps(result))
    assert result["syndrome_residual"]==0 and result["exact_saved_correction_match"]


if __name__=="__main__":main()
