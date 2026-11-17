"""Declared bridge scores, uncertainty, configuration controls, and decisions."""
from collections import defaultdict
from scipy.stats import beta, binom
from common import *


def interval(k, n, alpha):
    return [0. if k == 0 else float(beta.ppf(alpha/2, k, n-k+1)),
            1. if k == n else float(beta.ppf(1-alpha/2, k+1, n-k))]


def upper_rate(k, n, alpha):
    return 1. if k == n else float(beta.ppf(1-alpha, k+1, n-k))


def quantile_interval(values, alpha, upper_only=False):
    ordered = np.sort(values)
    n = len(ordered)
    lo = int(binom.ppf(alpha/2, n, .95))
    hi = int(binom.ppf(1-(alpha if upper_only else alpha/2), n, .95))+1
    result = [0. if not lo else float(ordered[lo-1]), None if hi > n else float(ordered[hi-1])]
    return result[1] if upper_only else result


def arrays(folder, name, setting=None):
    output, metadata = [], []
    for session in range(3):
        path = ROOT/"results"/f"session_{session}"/folder/(name+("__"+setting if setting else "")+".npz")
        with np.load(path) as a:
            output.append({key: a[key] for key in a.files})
        metadata.append(read(path.with_suffix(".json")))
    return {key: np.concatenate([r[key] for r in output]) for key in output[0]
            if key != "correction_columns"}, metadata, output


def main():
    corpus = read(ROOT/"corpus.json")
    predictions = read(ROOT/"bridge_predictions.json")
    summaries, raw, profiling = [], {}, {}
    session_summaries = [read(ROOT/"results"/f"session_{s}"/"session_summary.json") for s in range(3)]
    for case in corpus:
        name = case["name"]
        prof, pm, _ = arrays("profiling", name)
        profiling[name] = dict(shots=len(prof["wall_ns"]), p95_ns=float(np.quantile(prof["wall_ns"], .95)),
             p95_upper_ns=quantile_interval(prof["wall_ns"], .05/19, upper_only=True),
             timed_decode_wall_ns=int(prof["wall_ns"].sum()), init_wall_ns=sum(r["init_wall_ns"] for r in pm))
        settings = ["whole30", "whole100"]+(["components30"] if name == "d5_q2_memory_none" else [])
        for setting in settings:
            data, meta, by_session = arrays("evaluation", name, setting)
            raw[name, setting] = data
            censored = any(r["censored"] for r in meta)
            n = len(data["wall_ns"])
            failures = int(data["logical_z_failure"].sum())
            alpha = .05/19 if setting != "components30" else .05
            row = dict(name=name, parent=case["parent"], setting=setting, blocks=case["blocks"],
                 p=case["p"], placement=case["placement"], source=case["source"], shots=n, censored=censored,
                 mean_wall_ns=float(data["wall_ns"].mean()), p95_wall_ns=float(np.quantile(data["wall_ns"], .95)),
                 mean_cpu_ns=float(data["cpu_ns"].mean()), p95_cpu_ns=float(np.quantile(data["cpu_ns"], .95)),
                 p95_wall_interval=None if censored else quantile_interval(data["wall_ns"], alpha),
                 logical_z_failures=failures, logical_z_fraction=failures/n,
                 logical_z_upper=None if censored else upper_rate(failures, n, alpha),
                 median_init_wall_ns=float(np.median([m["init_wall_ns"] for m in meta])),
                 sessions=[dict(shots=len(a["wall_ns"]), mean_wall_ns=float(a["wall_ns"].mean()),
                     p95_wall_ns=float(np.quantile(a["wall_ns"], .95)), p95_cpu_ns=float(np.quantile(a["cpu_ns"], .95)),
                     logical_z_fraction=float(a["logical_z_failure"].mean())) for a in by_session])
            row["screen_qualified"] = not censored and row["logical_z_upper"] <= .01
            row["session_p95_max_min"] = max(r["p95_wall_ns"] for r in row["sessions"])/min(r["p95_wall_ns"] for r in row["sessions"])
            summaries.append(row)
    lookup = {(r["name"], r["setting"]): r for r in summaries}
    controls = []
    for case in corpus:
        for alternative in (["whole100", "components30"] if case["name"] == "d5_q2_memory_none" else ["whole100"]):
            name = case["name"]
            base, alt = lookup[name, "whole30"], lookup[name, alternative]
            a, b = raw[name, "whole30"], raw[name, alternative]
            assert len(a["wall_ns"]) == len(b["wall_ns"])
            improved = int(np.sum(a["logical_z_failure"] & ~b["logical_z_failure"]))
            worsened = int(np.sum(~a["logical_z_failure"] & b["logical_z_failure"]))
            ia = interval(improved, base["shots"], .05/(19*2))
            ib = interval(worsened, base["shots"], .05/(19*2))
            controls.append(dict(name=name, alternative=alternative, shots=base["shots"],
                 p95_wall_ratio=alt["p95_wall_ns"]/base["p95_wall_ns"],
                 mean_wall_ratio=alt["mean_wall_ns"]/base["mean_wall_ns"],
                 p95_cpu_ratio=alt["p95_cpu_ns"]/base["p95_cpu_ns"],
                 mean_cpu_ratio=alt["mean_cpu_ns"]/base["mean_cpu_ns"],
                 logical_improved=improved, logical_worsened=worsened,
                 paired_logical_difference_interval=None if base["censored"] else [ib[0]-ia[1], ib[1]-ia[0]],
                 session_p95_wall_ratios=[v["p95_wall_ns"]/u["p95_wall_ns"] for u,v in zip(base["sessions"], alt["sessions"])],
                 correction_disagreements=int(np.any(a["corrections_packed"] != b["corrections_packed"], axis=1).sum())))
    policies = sorted(next(iter(predictions.values())))
    scores = []
    for model in policies:
        for t, target in enumerate(TARGETS):
            by_parent = defaultdict(list)
            for case in corpus:
                row = lookup[case["name"], "whole30"]
                if not row["censored"]:
                    actual = row["mean_wall_ns" if t == 0 else "p95_wall_ns"]
                    by_parent[case["parent"]].append(abs(np.log(predictions[case["name"]][model]["raw_ns"][t]/actual)))
            scores.append(dict(model=model, target=target, heldout_parent_error_factor=float(np.exp(np.mean([np.mean(v) for v in by_parent.values()]))),
                 parent_mae_log={g: float(np.mean(v)) for g,v in by_parent.items()}))
    pairs = defaultdict(list)
    for case in corpus:
        if case["source"] != "old_exact":
            pairs[case["parent"], case["p"]].append(case)
    decisions = []
    for (parent, noise), cases in sorted(pairs.items()):
        assert len(cases) == 2 and cases[0]["ticks"] == cases[1]["ticks"]
        eligible = [case for case in cases if lookup[case["name"], "whole30"]["screen_qualified"]]
        row = dict(parent=parent, p=noise, candidates=[c["name"] for c in cases],
             eligible=[c["name"] for c in eligible], eligibility_is_retrospective_calibration_screen=True,
             quantum_speedup_claimed=False, choice_is_nontrivial=len(eligible) == 2, policies={})
        if eligible:
            oracle = min(eligible, key=lambda c: (lookup[c["name"], "whole30"]["p95_wall_ns"], c["name"]))
            oracle_cost = lookup[oracle["name"], "whole30"]["p95_wall_ns"]
            row.update(point_oracle=oracle["name"], point_oracle_p95_ns=oracle_cost)
            best_ci = lookup[oracle["name"], "whole30"]["p95_wall_interval"]
            others = [lookup[c["name"], "whole30"]["p95_wall_interval"] for c in eligible if c["name"] != oracle["name"]]
            row["cost_order_resolved_by_intervals"] = bool(others and best_ci[1] is not None and all(best_ci[1] < ci[0] for ci in others))
            for policy in policies+["profile_point", "profile_upper"]:
                def value(case):
                    if policy.startswith("profile_"):
                        v = profiling[case["name"]]["p95_ns" if policy == "profile_point" else "p95_upper_ns"]
                        return float("inf") if v is None else v
                    return predictions[case["name"]][policy]["raw_ns"][1]
                selected = min(eligible, key=lambda c: (value(c), c["name"]))
                cost = lookup[selected["name"], "whole30"]["p95_wall_ns"]
                row["policies"][policy] = dict(selected=selected["name"], measured_p95_ns=cost,
                     point_regret_factor=cost/oracle_cost, point_regret_ms=(cost-oracle_cost)/1e6)
        decisions.append(row)
    admission = []
    for budget in BUDGET_MS:
        truth = {}
        for case in corpus:
            actual = lookup[case["name"], "whole30"]
            values = raw[case["name"], "whole30"]["wall_ns"]
            k = int(np.sum(values > budget*1e6))
            truth[case["name"]] = dict(miss_fraction=k/len(values),
                 interval=None if actual["censored"] else interval(k, len(values), .05/(19*len(BUDGET_MS))))
        for policy in [m+"/"+mode for m in policies for mode in ("raw", "padded")]+["profile_point", "profile_upper"]:
            counts = dict(admitted=0, confident_false_admissions=0, confident_conservative_rejections=0, unresolved_truth=0,
                          qualified_admitted=0, qualified_confident_false_admissions=0, qualified_confident_conservative_rejections=0)
            details = []
            for case in corpus:
                name = case["name"]
                if policy.startswith("profile_"):
                    estimate = profiling[name]["p95_ns" if policy == "profile_point" else "p95_upper_ns"]
                else:
                    model, mode = policy.split("/")
                    estimate = predictions[name][model][mode+"_ns"][1]
                admitted = estimate is not None and estimate <= budget*1e6
                ci = truth[name]["interval"]
                false = bool(ci and admitted and ci[0] > .05)
                conservative = bool(ci and not admitted and ci[1] < .05)
                qualified = lookup[name, "whole30"]["screen_qualified"]
                counts["admitted"] += int(admitted)
                counts["confident_false_admissions"] += int(false)
                counts["confident_conservative_rejections"] += int(conservative)
                counts["unresolved_truth"] += int(ci is None or ci[0] <= .05 <= ci[1])
                counts["qualified_admitted"] += int(admitted and qualified)
                counts["qualified_confident_false_admissions"] += int(false and qualified)
                counts["qualified_confident_conservative_rejections"] += int(conservative and qualified)
                details.append(dict(name=name, admitted=admitted, screen_qualified=qualified, **truth[name]))
            admission.append(dict(budget_ms=budget, policy=policy, **counts, details=details))
    old = {r["name"]: r for r in read(STUDY/"results/case_summaries.json")}
    new = {r["name"]: r for r in read(STUDY/"stress_gate/results/discovery_summaries_reviewed.json")}
    references = []
    for case in corpus:
        name = case["name"]
        historic = old.get(name) if case["source"] == "old_exact" else new.get(name.removeprefix("bridge_"))
        if historic and not historic.get("censored", False):
            current = lookup[name, "whole30"]
            hp = historic["p95_ns"] if name in old else historic["p95_wall_ns"]
            hm = historic["mean_ns"] if name in old else historic["mean_wall_ns"]
            references.append(dict(name=name, old_exact=case["source"] == "old_exact",
                 historical_p95_ns=hp, current_p95_ns=current["p95_wall_ns"], p95_current_historical_ratio=current["p95_wall_ns"]/hp,
                 mean_current_historical_ratio=current["mean_wall_ns"]/hm))
    policy_regret = []
    nontrivial = [r for r in decisions if r["choice_is_nontrivial"]]
    for policy in policies+["profile_point", "profile_upper"]:
        by_parent = defaultdict(list)
        for decision in nontrivial:
            by_parent[decision["parent"]].append(np.log(decision["policies"][policy]["point_regret_factor"]))
        policy_regret.append(dict(policy=policy, nontrivial_pairs=len(nontrivial),
             resolved_pairs=sum(r["cost_order_resolved_by_intervals"] for r in nontrivial),
             parent_balanced_point_regret_factor=None if not by_parent else float(np.exp(np.mean([np.mean(v) for v in by_parent.values()]))),
             point_oracle_matches=sum(r["policies"][policy]["selected"] == r["point_oracle"] for r in nontrivial)))
    result = dict(client_analysis_date="2026-11-15", development_calibration_only=True,
         physical_evaluation_shots=sum(s["physical_evaluation_shots"] for s in session_summaries),
         evaluation_decoder_calls=sum(s["evaluation_decoder_calls"] for s in session_summaries),
         physical_profiling_shots=sum(s["physical_profiling_shots"] for s in session_summaries),
         physical_warmup_shots=sum(s["physical_warmup_shots"] for s in session_summaries),
         censored_cases=[r["name"] for r in summaries if r["setting"] == "whole30" and r["censored"]],
         summaries=summaries, paired_controls=controls, model_scores=scores, profiling=profiling,
         schedule_decisions=decisions, policy_regret=policy_regret, budget_sweep=admission, historical_bridge=references,
         quality_and_time_intervals_are_separate_families=True, intervals_assume_iid_stable_context=True,
         reserved_test_parents_used=False, frozen_predictions_updated=False)
    save(ROOT/"bridge_analysis.json", result)
    print(json.dumps({key: result[key] for key in ("physical_evaluation_shots", "evaluation_decoder_calls", "physical_profiling_shots", "censored_cases", "policy_regret", "model_scores")}, indent=2))


if __name__ == "__main__":
    main()
