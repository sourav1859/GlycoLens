# Graphify Compatibility and Safety

## Current project status

See `docs/tooling/graphify.md` for the inspected upstream ref and current machine blocker. The expected official package is `graphifyy`, while the executable is `graphify`.

## Required checks

- Python is 3.10 or later.
- An isolated installer such as `pipx` or `uv` is available.
- `graphify --version` and `graphify --help` succeed.
- `.gitignore` and `.graphifyignore` exclude sensitive and generated paths.
- The graph root resolves to the GlycoLens repository.
- Existing Git hooks are inspected before any hook installation.

## Data boundary

Local AST code extraction and semantic document/media extraction have different network implications. Start with code-only extraction. Treat any configured model backend as a possible external data transfer and require explicit approval before using it on repository documents.

Graph output is advisory. Confirm architecture, safety, and behavior claims against the cited source file and current diff.
