---
name: glycolens-change-delivery
description: Deliver a scoped GlycoLens implementation through acceptance criteria, context inspection, tests, verification, documentation, review, and measurement.
---

# GlycoLens Change Delivery

1. Define observable acceptance criteria before editing.
2. Read `AGENTS.md` and the two mandatory introductory planning documents once per focused task unless they change. Use the impact map to open only affected specialized planning documents, then inspect current code, tests, and Graphify context when useful.
3. Plan a small reversible change. Review API, security, privacy, accessibility, and observability implications where relevant.
4. Write a failing behavior test first when the requirement is clear and the layer is practical.
5. Implement only the requested behavior and preserve adapter and modular-monolith boundaries.
6. Run the narrowest real commands from [references/verification-ladder.md](references/verification-ladder.md) that prove the behavior. Reuse valid planning, test, Graphify, and diff evidence produced in the current task; do not rerun passed checks unless invalidated.
7. Update affected documentation and record reproducible improvement evidence when a measurable claim is made.
8. Inspect the complete diff for correctness, secrets, health data, generated output, and accidental scope.
9. Perform one final documentation review and one final Graphify refresh after relevant edits, first checking whether a hook already refreshed it. Disclose any blocker.

This skill coordinates delivery. Complete straightforward steps directly instead of spawning overlapping skills or agents.

Never push, merge, deploy, rotate secrets, or mutate external services without explicit authorization. Use GSD-inspired practices without requiring or installing the GSD-Pi runtime.
