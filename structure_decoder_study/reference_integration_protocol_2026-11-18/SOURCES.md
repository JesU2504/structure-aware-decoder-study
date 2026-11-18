# Primary semantics and local identities

Checked 18 November 2026. The local environment and source hashes in
environment.json/local_ps_source.json are authoritative for a future entry;
web documentation supplies general semantics, not a claim of actual integration.

- [Python subprocess](https://docs.python.org/3.12/library/subprocess.html):
  Popen polling/waiting and return-code handling; process creation and timeout
  handling cannot be treated as instantaneous wall-clock guarantees.
- [Python signal execution](https://docs.python.org/3.12/library/signal.html#execution-of-python-signal-handlers):
  Python handles signals at interpreter execution points, so a native call can
  defer handling; a handler exception can interrupt Python's returning path.
- [SciPy 1.17 milp](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.milp.html):
  the public MILP interface, integer domains, time/node options and returned
  statuses. The public signature has no initial-incumbent argument. A numerical
  bound is not independently verified constructive evidence.
- Local Darwin ps(1), /usr/share/man/man1/ps.1: stat's leading process states
  and TIME's user+system CPU meaning. Manual identity and short excerpts are
  frozen in local_ps_source.json; the native entry must observe actual states.

The web Python3.12 documentation currently serves patch3.12.16, while the
captured interpreter is3.12.12. This preparation does not silently upgrade it.
The installed direct HiGHS Python wrapper and native core are separately
identified; a version string alone is not the environment gate.

Historical evidence comes from the immutable reference probe and timeout-
repair folders. Their manifests remain part of the prospective input ledger.
No new literature novelty search or scientific result is implied here.
