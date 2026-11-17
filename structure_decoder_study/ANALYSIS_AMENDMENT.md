# Analysis implementation correction

The original frozen `analyze.py` stopped on its first metadata merge, before
fitting models or producing results. Both the case metadata and feature dictionary
contain `distance`; Python's `dict(..., **a, **b)` rejects duplicate keyword names.

The versioned replacement `analyze_v2.py` uses a dictionary literal merge. Both
copies of distance have the same value. This changes only output-row assembly;
feature sets, targets, folds, regularization, resampling, decision diagnostics,
and plotting logic are unchanged. The original file and frozen config are
retained. No timing observations are rerun or excluded.

The amendment's hashes are recorded in `analysis_amendment.json`. Reproduce the
analysis using `analyze_v2.py`; `analyze.py` is preserved as the original failed
implementation. The raw-file audit verifies both the frozen original and the
versioned correction.
