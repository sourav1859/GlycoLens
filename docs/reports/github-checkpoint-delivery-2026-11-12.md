# GitHub checkpoint delivery — November 12, 2026

## Authorization and scope

The user explicitly authorized committing and pushing the pending changes to
GitHub and refreshing Graphify. This supersedes the earlier local-review hold for
this checkpoint. Later source pushes and public deployment still require their
own authorization. Scratch replay remains deferred.

Publish the cloud-backed responsive webapp implementation, migrations, tests,
CI definitions, local Compose runtime and living documentation on the existing
`main` branch. Keep phase acceptance partial: the current 146-case ledger includes
22 PASS, 87 PARTIAL, 34 BLOCKED and 3 NOT_RUN. No phase, hosting or scientific gate
is closed by publishing source.

## Validation and privacy boundary

The [November 12 review](demo-logout-compose-review-2026-11-12.md) records 171
offline Python passes plus one opt-in skip, 24 frontend unit passes, 26 isolated
desktop/mobile browser passes, lint/types/build, real Linux simulator/CPU model
smoke and restart/storage checks. Reuse this valid evidence; no paid/provider or
cloud-mutation rerun is required for publishing the unchanged implementation.
The final publication review separately checks source hashes, current frontend
types, staged whitespace, private-file exclusions and exact private-value leaks.

Private environment files, credentials, password-recovery helpers, private source
artifacts, model weights, datasets and generated Graphify output remain ignored.
The personal-account recovery helper is local-only and is not application source.

## Graphify delivery

Refresh local AST/Markdown nodes and source-backed current semantic relationships
after documentation edits. This uses no external semantic API. Retain the existing
generated-output exclusions: Graphify is a local developer aid, not application
GraphRAG or acceptance evidence. Actual counts and source hashes are recorded in
ignored `graphify-out/semantic-refresh-evidence.json`.

The explicit refresh replaces the duplicate asynchronous Graphify post-commit
rebuild for this commit only; normal hooks remain installed. No test/security
hook is bypassed. Git commit and remote verification results are reported after
publication, without embedding a self-referential commit hash in this source.
