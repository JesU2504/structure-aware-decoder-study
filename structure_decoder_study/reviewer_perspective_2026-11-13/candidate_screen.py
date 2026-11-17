"""Describe existing same-program pairs; tick count is not physical duration."""
from pathlib import Path
from collections import Counter
import json
import stim

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent


def main():
    summaries = json.loads((STUDY/"stress_gate/results/discovery_summaries_reviewed.json").read_text())
    output = []
    for program in [f"q4_P{i:02}" for i in range(8)]:
        records = [r for r in summaries if r["program"] == program and r["distance"] == 5
                   and r["rounds"] == 10 and r["p"] == .001]
        pair = []
        for record in records:
            circuit = stim.Circuit((STUDY/"stress_gate/circuits"/(record["name"]+".stim")).read_text())
            counts = Counter()
            for op in circuit.flattened():
                if op.name not in ("DETECTOR", "OBSERVABLE_INCLUDE", "QUBIT_COORDS", "SHIFT_COORDS"):
                    counts[op.name] += len(op.targets_copy()) if op.targets_copy() else 1
            pair.append(dict(name=record["name"], placement=record["placement"], ticks=circuit.num_ticks,
                 detectors=circuit.num_detectors, measurements=circuit.num_measurements,
                 p95_ms=record["p95_wall_ns"]/1e6, deadline_ms=record["budget_ns"]/1e6,
                 padded_admitted=record["padded_admitted"], logical_z_fraction=record["logical_z_failure_fraction"],
                 instruction_target_counts=dict(counts)))
        assert len(pair) == 2
        output.append(dict(program=program, variants=pair, same_tick_count=pair[0]["ticks"] == pair[1]["ticks"],
             same_instruction_target_counts=pair[0]["instruction_target_counts"] == pair[1]["instruction_target_counts"],
             both_measured_p95_below_budget=all(row["p95_ms"] < row["deadline_ms"] for row in pair)))
    (ROOT/"compiler_candidate_screen.json").write_text(json.dumps(dict(post_hoc=True,
         tick_counts_are_not_a_hardware_timing_model=True, pairs=output), indent=2, sort_keys=True)+"\n")
    print(f"Checked {len(output)} same-program schedule pairs")


if __name__ == "__main__":
    main()
