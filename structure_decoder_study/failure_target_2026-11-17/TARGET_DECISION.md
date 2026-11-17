# Target decision and publication gates — 17 November 2026

**Choose logical decoding failure as the first failure type to investigate.**
The preferred candidate is low-weight fault injection in the circuit-level
BB [[144,12,12]] memory experiment. Its selection is conditional on exact
reproducibility. It is a diagnostic benchmark, not an established new paper
contribution or an automatic replacement for the compiler-cost objective.

## Why this target

[Trapping Sets of Detector Error Models](https://arxiv.org/html/2608.11516v1)
reports failures on small injected fault supports in a 12-round BB144 memory
experiment: weight four for RelayBP and ImpulseBP, and also weight three for
ELMS. It already connects circuit-DEM topology with error-floor behavior.
Thus finding trapping-set failures or predicting their error floor is prior
work, not our novelty. Its findings do not establish that our BP+LSD backend
fails on the same supports.

I prefer this candidate to selecting a deadline after looking at our CPU times,
or increasing noise until a large fraction of shots fail. It offers a specific
documented failure mechanism. It is still only one memory task and one measured
logical sector; it does not by itself test multi-patch compiler choices.

## Work completed here

The pinned source subset and `ENTRY_PROTOCOL.md` preceded construction-helper
execution. No enumeration entry point, C++ search or decoder was run. The public
generator produced 936 detectors and 12 logical observables. Its DEM contains
10,368 raw independent error entries and 8,784 distinct detector/logical
signatures. H has 30,672 nonzero entries. Independent GF(2) checks verified the
CSS and logical conditions; no distance certificate was computed.

All 32 noiseless circuit validation samples were zero. All 256 saved DEM
validation samples reconstructed their syndromes and logical flips from both
raw and merged fault vectors. These checks validate the mapping; they are not
decoder trials or estimates of physical logical-error rate.

The original probe correctly returned **fail** on one of its 20 checks. The
repository converter uses addition for duplicate-signature probabilities.
Independent events with identical signatures combine by odd parity:

`p_merged = (1 - product_i(1 - 2*p_i))/2`.

At p=0.001, 1,584 columns differ. The largest absolute discrepancy is
4.61322e-6 and the largest relative discrepancy is 0.150808%. We saved both
the repository additive priors and independently verified exact parity priors.
The remaining 19 checks passed. The later audit confirmed the discrepancy;
it did not overwrite the initial failure or redefine it as a complete pass.
No effect on decoding outcomes has been measured. Approximate decoder priors
are not evidence that the paper's conclusions are wrong. The previous study's
converter already performs exact parity merging (`study.py:156`).

Artifact access is partial. `public_access_audit.json` records all six available
commit trees, the main branch and zero releases in the inspected repository.
We found a generator and BB108 trapping-set catalogues, but no labeled BB144
failure witness or decoder evaluation runner there. This does not prove that
the artifacts are globally unavailable. The authors' public
[RelayBP implementation](https://github.com/trmue/relay) supplies a possible
backend, but its defaults do not establish the trapping-set paper's full setup.
Only its metadata/documentation was inspected; it was not installed or run.

The first source fetch was blocked by network restrictions and left an invalid
empty-file snapshot. That was caught before import or execution. The invalid
snapshot is preserved as `first_fetch_failure.json`. A validated download then
checked byte counts, Git blob IDs and SHA256 hashes for all five files. The
source manifest describes that fetch-time state; construction execution is
recorded separately in the probe result. The independent audit verified all 16
previous result manifests without changing their contents.

## Novelty boundary

[Adaptive decoding through decoder disagreement](https://arxiv.org/html/2609.37629v1)
already uses a decoder-internal risk signal to route selected instances to
deeper post-processing, including BB144 circuit-level experiments and measured
serial cost. Its methods also separate failure risk from the stronger search's
ability to repair a case. Therefore generic risk prediction, selective rescue,
or that distinction alone is insufficient novelty for us. A different feature
or a different regressor alone is not a persuasive response to this overlap.

| Proposed statement | Current assessment |
| --- | --- |
| Some small fault patterns defeat practical iterative decoders | Established prior work; reproduce as a control |
| Topology affects these failures | Established prior work |
| Spend more decoding effort on risky shots | Close prior work with public implementation |
| Our tested graph summaries improve compiler decisions | Not supported by the earlier study |
| A reproducible correctness–cost failure exposes a gap in an existing compiler-facing estimate | Candidate question; neither an observed result nor established novelty |

## What to do next, in order

1. **Obtain an exact reproducible failure case.** The entry packet must identify
   the circuit/DEM hash, ordered H and L, priors, injected support, decoder version,
   precision, iteration/restart settings, random seed and returned correction.
   Begin with one failing support and one comparable successful control. Public
   aggregate tables and a topology drawing are insufficient to identify columns.
   Do not launch the full trapping-set enumeration to fill this access gap.
   A bounded independent search could create a new witness, but must be labeled
   a new experiment, not a reproduction of an unspecified published support.
2. **Replay and classify before timing.** Check H e_hat against H e separately
   from L e_hat against L e. Record nonconvergence and syndrome-valid logical
   errors separately. For a randomized backend, replay the same support over
   declared independent seeds and retain every outcome. Any claim that the
   injected support is guaranteed correctable needs a certificate applicable
   to this exact circuit/fault model, rather than its nominal code label.
3. **Rule out a weak or mismatched baseline.** Reproduce published settings first;
   compare additive and exact priors as an explicit sensitivity experiment.
   Check a declared iteration/restart budget ladder and at least one established
   stronger backend on the same faults. Extra iterations need not improve
   accuracy. Keep implementation precision, randomization and post-processing
   visible. Choose settings on development cases and freeze them before a later
   confirmation panel. Do not describe this as neural-network undertraining.
4. **Test relevance to cost modeling.** Ask whether repairing verified failures
   creates a consequential correctness–cost tradeoff that existing estimates or
   strong simple baselines miss. Count feature extraction, decoder initialization,
   fallback and profiling costs. Compiler-visible features are fixed for all
   shots of a fixed circuit/DEM; they cannot rank its individual fault patterns.
   Runtime syndrome or decoder-trace signals would change the interface and
   research scope and require a separate comparison with adaptive-decoding work.
5. **Commit to a paper question only after that result and a focused overlap
   check.** If cost and correctness do not interact usefully, or a known baseline
   handles the issue, stop this branch. A decoder failure alone is not enough.

Later case/control stress data must remain separate from a natural-noise sample.
Match fault weight and syndrome weight where possible and report residual
differences in support probability and location. Neither matched controls nor
oversampled harmful patterns estimate natural LER or latency quantiles without
appropriate sampling weights. Repeated seeds and overlapping/translated fault
supports are not independent circuit families. Any later generalization test
must separate related supports and reserve genuinely untouched workloads.

**Decision now:** generator access passes, exact-prior equality to the public
helper fails in a quantified way, exact published-failure reproduction remains
unestablished, and method-level novelty remains open. No new decoder calls,
model fits, training samples or reserved evaluation workloads were used here.
