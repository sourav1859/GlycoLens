# Repository-Scoped Codex Skills

GlycoLens keeps shared agent workflows under `.agents/skills/` so repository-specific decisions remain reviewable with the project.

| Skill | Use |
|---|---|
| `graphify` | Check, build, update, and query the local repository knowledge graph safely. |
| `glycolens-docs-governance` | Keep the ten planning documents and repository guidance synchronized with change. |
| `glycolens-architecture-review` | Evaluate consequential architecture and integration decisions. |
| `glycolens-change-delivery` | Deliver focused changes through acceptance criteria, tests, verification, and documentation. |
| `glycolens-test-architect` | Derive risk-based test strategies and implementations. |
| `glycolens-pr-guardian` | Review diffs and draft local commit or pull-request text without external mutation. |
| `glycolens-impact-ledger` | Record reproducible before/after improvements and defensible portfolio claims. |
| `glycolens-safety-review` | Review medical-facing behavior, health data, authorization, and release safety. |

Each `SKILL.md` uses only `name` and `description` in YAML frontmatter. Supporting references contain project-specific maps and checklists; reusable output templates live in `assets/`.

Validate all immediate skill directories with `python scripts/quality/validate_skills.py`. The command requires Python 3.10 or later.
