# Guarded cloud development runners

Use `python -m scripts.dev.cloud_preflight` for a redacted read-only readiness report.
The integration modules `cloud_integration`, `account_integration`, `meal_integration`,
`source_integration`, `privacy_integration` and `scenario_integration` default to no
network unless `--allow-cloud` is explicit. Each requires the exact development
URL/ref and ignored credentials, run-tagged synthetic accounts, bounded requests
and recorded-ID cleanup. Pass `--output <redacted-report.json>`. Source/scenario
runners also require reviewed cached simulator/model runtimes; no paid LLM calls.

Never run historical local reset/Configure-LocalDemo/check_m2_application helpers
against the cloud environment. See the implementation report and case ledger for
actual coverage and limitations. New changes are local for review, not pushed.
