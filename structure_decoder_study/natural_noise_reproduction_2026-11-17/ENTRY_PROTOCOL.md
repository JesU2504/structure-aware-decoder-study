# Published-regime reproduction entry gate — 17 November 2026

Authorization: prepare and run the supervisor-recommended experiment if its
construction/conversion checks pass, then obtain an independent AI supervisor
review. This is a controlled replication, not a new method or publication claim.

Target: public Adaptive-qLDPC commit
`8cc32014a6461bb8f241f47f62a7e74f63817738`, BB [[144,12,12]] Z-memory,
24 rounds, p=0.007. The paper reports 1,800 detectors, 12 logical observables,
12,240 fault columns and rank(H)=1,794. These are verification targets, not
assumed validated results.

1. Download a small pinned source subset, validating byte counts, Git blob IDs
   and SHA256 hashes before accepting it. Read imports and called functions.
   Do not run the upstream experiment entry point or its expensive sweeps.
2. Isolate imports/configuration side effects within this new directory. Reuse
   installed packages; install nothing or change frozen study artifacts.
3. Build only the specified circuit and extract the source DEM/H/L/priors using
   documented helper APIs after reviewing them. Independently check CSS/logical
   conditions, GF(2) rank, zero-noise behavior, and complete parity signatures
   including repeated targets across separator hints. Compare raw columns and
   prior clipping explicitly; preserve any discrepancy.
4. Verify raw-DEM fault-vector reconstruction against Stim on 64 fixed-seed DEM
   validation samples and 16 noiseless circuit validation samples. Also use
   synthetic repeated-target cases to check the independent converter's parity
   behavior. These are validation data, not the later experiment sample.
5. Stop before decoder experiments on unexplained mismatches in construction or
   semantics. Obtain the supervisor's review of such an entry failure rather
   than silently replacing a converter and calling it an exact reproduction.

If entry passes, freeze a separate execution protocol, all inputs/source hashes,
two sampler seeds and job order before decoder calls: 512 natural circuit-noise
shots (2 x 256), published BP20+OSD0 plus paired BP+LSD30/100 controls. At most
1,800 decoder calls, 1,200 measured CPU seconds and 1,800 wall seconds. Include
adapters and any predeclared selected-case replay/forced-LSD controls in those
limits. Record invalid correction, syndrome-valid logical error, BP stage
nonconvergence and resource censoring separately. No new predictor or manuscript.

Then independently audit outputs and ask the AI supervisor to check the setup,
results and conclusions. Preserve both successful and failed entry checks.
