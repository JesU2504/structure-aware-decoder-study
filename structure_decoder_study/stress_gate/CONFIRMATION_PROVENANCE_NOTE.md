# Confirmation metadata snapshot timing

The fixed-prefix amendment and its implementation were written before launching
confirmation. The first command intended to hash those files and the backend
binaries failed on a Python import-name collision. The orchestration then
launched the unchanged confirmation measurement command.

The corrected snapshot uses importlib and explicitly records
`recorded_after_confirmation_launch: true` in `confirmation_lock.json`. It must
not be represented as a pre-launch hash lock. The prefix declaration and script
already existed before launch; no confirmation outcomes were inspected to choose
or alter their rules. The original pre-timing lock, fixed predictors, selection,
sampling protocol, and primary analysis are unchanged. This is internal
provenance, not external preregistration.
