---
name: glycolens-change-delivery
description: Deliver a scoped GlycoLens implementation through acceptance criteria, context inspection, tests, verification, documentation, review, and measurement.
---

# GlycoLens Change Delivery

1. Define observable acceptance criteria before editing.
2. Read `AGENTS.md`, affected planning documents, current code, tests, and Graphify context when available.
3. Plan a small reversible change. Review API, security, privacy, accessibility, and observability implications where relevant.
4. Write a failing behavior test first when the requirement is clear and the layer is practical.
5. Implement only the requested behavior and preserve adapter and modular-monolith boundaries.
6. Run the real commands selected from [references/verification-ladder.md](references/verification-ladder.md). Do not invent commands or claim unrun checks.
7. Update affected documentation and record reproducible improvement evidence when a measurable claim is made.
8. Inspect the complete diff for correctness, secrets, health data, generated output, and accidental scope.
9. Refresh Graphify after supported changes, or disclose why it was not refreshed.

Never push, merge, deploy, rotate secrets, or mutate external services without explicit authorization. Use GSD-inspired practices without requiring or installing the GSD-Pi runtime.
