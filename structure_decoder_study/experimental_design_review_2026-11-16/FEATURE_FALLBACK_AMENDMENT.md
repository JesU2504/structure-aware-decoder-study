# Arithmetic feature-family fallback check

16 November 2026. Added after the wider-grid outcomes were inspected. This is
explicitly post hoc development analysis, not another fitted model or independent
confirmation. No additional fit, feature, target or decoder work is permitted.

Adding coordinates to an isotropic RBF changes its distance metric. Its augmented
feature family does not automatically reproduce the density8 kernel by assigning
zero weight to the new coordinates. Thus a failed graph16 model is not a test of
all ways of using that extra information.

Using the already-saved original- and extended-grid fits, compare a simple
training-only selector: for each target and outer fold, choose rbf_density8 or
rbf_graph16 by the smaller saved minimum inner group-validation loss. Break ties
in favor of density8. Evaluate the selected candidate's saved outer predictions.
Report all three domains, both targets and both grids. Outer test errors must
not enter the choice. Also report the selected families for inspected bridge
predictions, with their established fold convention.

This tests one baseline-containing family selector, not arbitrary structure
weighting, optimal representation, novelty or compiler usefulness. It has no
population guarantee of matching the base-only outer error; model-selection
variance can hurt. A continuous feature-weighted kernel remains a different,
unrun hypothesis, not an automatic next search.
