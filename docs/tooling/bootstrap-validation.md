# Local Bootstrap Validation Record

- Date: September 27, 2026
- Branch: `chore/local-development-bootstrap`
- Starting and current commit: `6bb4ecd33ca2851c87a524051f0ed947ee91d1da`
- Remote: `https://github.com/sourav1859/GlycoLens.git`

## Tool preflight

| Tool | Result |
|---|---|
| Git | Passed: 2.45.1.windows.1 |
| Windows PowerShell | Passed: 5.1.26100.9549 |
| PowerShell 7 (`pwsh`) | Missing |
| Python | Passed: 3.12.5, 64-bit |
| pipx | Passed: 1.7.1 |
| Node.js | Passed: 22.14.0 |
| npm | Passed: 10.9.2 |
| pnpm/yarn | Blocked in the sandbox by Corepack profile-file access; not required for this bootstrap |
| Codex CLI | Available: 0.155.0-alpha.16.3 |

## Validation results

| Check | Result |
|---|---|
| Expected remote, clean starting tree, local bootstrap branch | Passed |
| `git diff --check` | Passed |
| Eight skill directories and exact frontmatter fields | Passed by PowerShell audit and the Python validator |
| `python scripts/quality/validate_skills.py` | Passed: eight skills, zero failures |
| Temporary invalid-fixture validator test | Not run |
| PowerShell syntax parsing | Passed for all eight Graphify scripts |
| Graphify exclusion check | Passed |
| Graphify readiness/status wrappers | Passed with Python 3.12.5 and Graphify 0.9.69 |
| Initial graph and explicit update | Passed: code-only graph with 578 nodes, 490 edges, and 94 communities after deterministic clustering refresh |
| Graphify wiki and query | Passed: 104 wiki articles written; representative query source-verified |
| Graphify hook | Passed: post-commit, post-checkout, and merge driver installed |
| Graphify watcher | Not started; launch remains an explicit foreground action |
| Required directories and documentation | Passed |
| Ten planning Markdown files present and non-empty | Passed |
| Representative ignore checks | Passed for secrets, raw data, weights, evaluation, benchmarks, Graphify, and Playwright output |
| Internal relative Markdown links | Passed targeted repository audit |
| Credential-like marker scan | Passed; no matches found |
| Presentation template | Passed: source copies matched SHA-256, copied file is non-empty, has an Office ZIP signature, and is not an LFS pointer |
| Named project presentation | Missing; no placeholder created |
| Existing product tests/builds | Not applicable; no product toolchain or implementation exists |
| GSD-Pi runtime and `.gsd/` state | Not installed or created |

## Graphify scope

Graphify is **ACTIVE for local code-only analysis**. Semantic document/media extraction remains disabled because it requires an explicitly approved backend and data boundary. The generated graph remains ignored and local.

## Git boundary

The bootstrap intentionally leaves all changes unstaged and uncommitted. Nothing was pushed and no GitHub repository state was changed.
