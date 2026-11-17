# Fixed natural-noise experiment — 17 November 2026

This protocol is written after construction checks and before any decoder calls
or experiment-shot generation. The entry passed all 24 checks: source and
independent H/L/priors match exactly; H is 1800 x 12240 with GF(2) rank 1794;
there are 12 logical-Z observables. There are no repeated error targets or
separator hints in this actual DEM and no probability clipping takes effect.
Sixteen noiseless and 64 DEM-validation samples passed. Preserve those checks.

## Scope and fixed sample

Reproduce the public Adaptive-qLDPC fast-path configuration at pinned commit
`8cc32014a6461bb8f241f47f62a7e74f63817738`: BB144 Z-memory, 24 extraction
rounds, p=0.007. The public generator measures **Z checks only**, on 144 data
and 72 ancilla qubits. This is its published-source experiment, not a full
both-check extraction circuit or a hardware fault-tolerance demonstration.

Draw exactly 256 natural circuit-noise shots for each Stim detector-sampler
seed **2026111731** and **2026111732**, ordered by seed block then index. Assign
case IDs 0..511. Save detector and actual logical-observable arrays once and
give precisely those inputs to all decoders. These are independent-noise samples
under the specified source circuit; they do not identify unique fault supports.
Save hashes of circuit/DEM/H/L/priors, source, protocol, runner, versions, samples,
seeds and all job assignments before any decoder call. This is a fixed small
replication, not an exact repeat of the paper's seeds or shot count.

The source figure reports 398/20000 fast-path logical failures at this point;
our sample is not guaranteed to contain a failure. Do not adjust seeds, p,
rounds, sample count or decoder settings in response to outcomes.

## Three paired configurations

Use installed ldpc 2.4.1, one thread, parallel BP updates, min-sum scale 0.625
and random schedule seed 0. The primary path is BP cap 20 plus OSD_0/order 0.
Assert public properties, and compare the native returned correction with the
`osd0_decoding` readout used by the upstream evaluator. Stop on unexplained
readout mismatch; do not count it silently as an algorithmic failure.

Controls are BP+LSD_0/order 0 at BP caps 30 and 100, bits_per_step=1,
always_run_lsd=False. These are different algorithmic budgets, not a matched-work
optimality comparison. All use identical raw-DEM column ordering and priors.

Match the source's persistent-decoder usage: one fresh instance per decoder per
seed block, six instances total for the main experiment. Within each block keep
case order 0..255. Shuffle the three configurations within each case with fixed
PCG64 job-order seed **2026111733**. No warmup shots beyond the separate declared
adapters below. Record initialization CPU/wall costs separately, service CPU/wall
costs on every call, first-call flags and total management costs. Absolute times
on this Apple CPU are not a reproduction of the paper's Xeon timings.

## Counted adapters, outcomes and replay

Before the main experiment use eleven planned adapter calls: each of the three
settings on zero and singleton-column-0 syndromes (six); primary OSD0 and forced
LSD0/LSD_CS2 on a three-bit repetition-check toy (three); the two forced settings
on the new BB singleton (two). Independently enumerate the toy's syndrome-valid
corrections and compare weighted scores. Verify nonempty LSD cluster statistics
on forced nonzero-syndrome calls, including a BP-converged toy. No adapter is
drawn from the 512 evaluation samples, and adapters count against the total cap.

Store every attempt, correction, BP decision, LLRs, BP convergence/iterations,
syndrome residual, predicted logical vector, actual vector and outcome. Keep
syndrome-valid logical errors separate from invalid returned corrections, BP
stage nonconvergence, exceptions and resource censoring. A BP nonconvergence
followed by correct post-processing is a correct full result. Correctness means
H e_hat = s **and** L e_hat = actual; equality to a hidden fault vector is neither
available nor required. The decoder receives neither actual logical labels nor
a true fault support. Record source/native-readout equivalence for the primary.

After all 1536 main calls, select the first at most eight primary failures
(invalid or logically wrong) by ascending case ID. For each choose one unused
primary-success control, preferring the same seed block, then closest syndrome
weight, then case ID. Selection does not consult control-decoder outcomes.
Log matching differences; matched selections are descriptive, not a random test
of rescue probabilities. Do not select only cases repaired by a control.

Replay all three configurations on fresh instances for each selected case
(at most 48 calls), requiring exact correction/BP/classification equality to the
persistent-instance result. Preserve mismatches and suspend deterministic
witness claims if they occur. Then apply existing forced LSD_0/order 0 and
LSD_CS/order 2 at BP30 on those cases (at most 32 calls). Collect statistics to
verify processing really ran. Zero syndromes bypass post-processing even with
the force option; record that explicitly. Save every rescue and regression.
This is not a reproduction of the paper's K1000 or full-1FV search.

## Resource and interpretation rules

Maximum 1800 decoder invocations, including adapters, replays and comparisons.
Planned maximum is 11+1536+48+32=1627. Stop before another decode when total run
CPU reaches 1200 s or wall time reaches 1800 s. Count imports, initialization,
evaluation and I/O in run totals. Flush a start/decode-start/completion journal
and every result; never silently drop slow or incomplete cases. A native call
can overrun a between-call cap. Stop on exceptions or adapter discrepancies.

If no primary failure appears, finish as inconclusive for a failure witness and
review reproduction differences; do not increase noise or sample more seeds.
If present, export the first selected independently verified logical-failure
packet and the paired outcomes. A repaired shot demonstrates that shot's recovery
only, not a bounded-distance guarantee. Broader repair headroom remains unknown
when these controls fail.

The final report will include all 512 paired outcomes (or clearly labelled
incomplete coverage), per-seed and pooled outcome counts, Wilson intervals for
this natural-noise sample if complete, rescue/regression transition counts and
descriptive service/initialization costs. Do not claim equality to the paper's
rate, superior general decoder performance, a natural extreme-tail guarantee,
new prediction accuracy, compiler benefit or publication novelty. No model
training, manuscript, hardware experiment or reserved test workload is involved.

Finally independently check saved outputs, repeat sampler generation at the
same fixed seeds as a deterministic provenance check, verify earlier manifests
unchanged and obtain an AI supervisor review of design, results and conclusions.
