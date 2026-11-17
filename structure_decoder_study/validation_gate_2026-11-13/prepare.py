"""Prepare the declared calibration bridge without timing decoder calls."""
import importlib.util
import sys
import time
from types import SimpleNamespace
from common import *


def main():
    assert not (ROOT/"preparation.json").exists(), "Prepared bridge is immutable"
    previous = verify_previous()
    sys.path.insert(0, str(STUDY))
    import study
    import stim
    spec = importlib.util.spec_from_file_location("validation_stress_source", STUDY/"stress_gate/stress.py")
    stress = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stress)
    old = {r["name"]: r for r in read(STUDY/"corpus.json")}
    programs = {p["id"]: p for p in read(STUDY/"stress_gate/programs.json")}
    cases = []
    for name in ("d5_q2_memory_none", "d5_q4_chain_spread", "d5_q4_cycle_late"):
        r = old[name]
        cases.append(dict(name=name, source="old_exact", parent="old/"+r["case"]["family"],
                          **r["case"], gates=r["gates"], events=r["event_rounds"],
                          literal_source=str((STUDY/"circuits"/(name+".stim")).relative_to(STUDY))))
    for program in ("q4_P00", "q4_P03", "q6_P00", "q6_P03"):
        p = programs[program]
        for noise in (.0003, .001):
            for placement in ("spread", "burst"):
                events = ([5]*len(p["gates"]) if placement == "burst" else
                          np.rint(np.linspace(1, 8, len(p["gates"]))).astype(int).tolist())
                name = f"bridge_{program}_d5_w10_p{str(noise).replace('.', '_')}_{placement}"
                cases.append(dict(name=name, source="new_parent_calibration", parent="new/"+program,
                     distance=5, blocks=p["blocks"], rounds=10, p=noise, placement=placement,
                     gates=p["gates"], events=events, canonical_map=p["canonical_map"]))
    assert len(cases) == 19
    invariance, checks = [], []
    for case in cases:
        if case["source"] == "old_exact":
            text = (STUDY/case["literal_source"]).read_text()
            circuit = stim.Circuit(text)
        else:
            circuit = stress.assemble(case["distance"], case["blocks"], case["rounds"], case["p"], case["gates"], case["events"])
            text = str(circuit)
        dem = circuit.detector_error_model()
        h, l, priors, mapping = study.convert(dem)
        f, _ = features(case["distance"], h, priors)
        original = study.features(SimpleNamespace(**{k: case[k] for k in ("distance", "rounds", "blocks")}), h, l, priors)
        assert all(np.isclose(f[c], original[c], rtol=1e-10, atol=1e-10) for c in BASE+STRUCTURE)
        if case["source"] == "old_exact":
            assert text == (STUDY/case["literal_source"]).read_text()
            assert all(np.isclose(f[c], old[case["name"]]["features"][c], rtol=1e-10, atol=1e-10) for c in BASE+STRUCTURE)
        rng = np.random.default_rng(seed("feature_invariance", case["name"]))
        for trial in range(3):
            rows, cols = rng.permutation(h.shape[0]), rng.permutation(h.shape[1])
            hp = h[rows][:, cols].tocsc()
            hp.sort_indices()
            fp, _ = features(case["distance"], hp, priors[cols])
            assert all(np.isclose(fp[c], f[c], rtol=1e-10, atol=1e-10) for c in DENSITY+STRUCTURE), case["name"]
        ideal = circuit.without_noise().compile_detector_sampler(seed=1).sample(32, append_observables=True)
        assert not ideal.any()
        dd, oo, ee = dem.compile_sampler(seed=seed("bridge_dem", case["name"])).sample(64, return_errors=True)
        merged = np.zeros((64, h.shape[1]), dtype=np.uint8)
        for col, destination in enumerate(mapping):
            if destination >= 0:
                merged[:, destination] ^= ee[:, col]
        assert np.array_equal((h@merged.T).T % 2, dd) and np.array_equal((l@merged.T).T % 2, oo)
        case.update(features=f, ticks=circuit.num_ticks, n_qubits=circuit.num_qubits)
        folder = ROOT/"circuits"
        folder.mkdir(exist_ok=True)
        (folder/(case["name"]+".stim")).write_text(text)
        (folder/(case["name"]+".dem")).write_text(str(dem))
        np.savez_compressed(folder/(case["name"]+".npz"), h_data=h.data, h_indices=h.indices, h_indptr=h.indptr,
             h_shape=h.shape, l_data=l.data, l_indices=l.indices, l_indptr=l.indptr, l_shape=l.shape, priors=priors)
        case["files"] = {suffix: sha(folder/(case["name"]+suffix)) for suffix in (".stim", ".dem", ".npz")}
        timings = [features(case["distance"], h, priors)[1] for _ in range(10)]
        case["feature_timing"] = {k: float(np.median([t[k] for t in timings])) for k in timings[0]}
        invariance.append(case["name"])
        checks.append(dict(name=case["name"], ideal=True, dem_reconstruction=True))
    save(ROOT/"corpus.json", cases)
    save(ROOT/"preparation.json", dict(previous_manifests_verified=previous, cases=len(cases),
         stable_descriptor_permutations_checked=len(invariance)*3, decoder_timings_collected=False,
         checks=checks, source_hashes={str(p.relative_to(STUDY)): sha(p) for p in
             (STUDY/"study.py", STUDY/"stress_gate/stress.py", ROOT/"common.py", ROOT/"prepare.py", ROOT/"PROTOCOL.md")}))
    print(f"Prepared {len(cases)} bridge configurations; no decoder timings collected", flush=True)


if __name__ == "__main__":
    main()
