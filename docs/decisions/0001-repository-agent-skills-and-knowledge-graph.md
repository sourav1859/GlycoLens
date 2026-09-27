# ADR 0001: Repository Skills and Developer Knowledge Graph

- Status: Accepted
- Date: 2026-09-27

## Context

GlycoLens needs repeatable documentation, architecture, delivery, testing, review, measurement, and safety workflows while remaining a small capstone repository. It also benefits from repository relationship queries, but product GraphRAG is explicitly outside the MVP.

## Decision

Maintain eight original repository-scoped Codex skills under `.agents/skills/`. Use Graphify only as an optional local developer knowledge graph with source verification and strict exclusions. Keep its generated output out of Git and separate it from the product database, retrieval design, and forecasting system.

Adopt selected general GSD-Pi practices—verify before completion, test-driven development when behavior is clear, security and API review, documentation synchronization, observability, accessibility, measurement, and structured review—without installing the GSD-Pi runtime or creating `.gsd/` state.

## Alternatives considered

- Informal conventions only: rejected because high-risk documentation and health-data boundaries need discoverable workflows.
- Full GSD-Pi runtime: rejected because its project state, worktree automation, model routing, and commit workflow exceed the bootstrap scope.
- Product GraphRAG: rejected for the MVP because structured SQL and pgvector better fit application retrieval, while Graphify serves only developer navigation.

## Consequences

- Skill definitions and supporting references require validation and maintenance.
- Graphify availability is conditional on local prerequisites and safe configuration.
- Graph results remain advisory and must be checked against source.
- The repository gains governance structure without adding product implementation or runtime dependencies.

## External references inspected

- Graphify `v8` documentation and MIT package metadata, inspected September 27, 2026: <https://github.com/Graphify-Labs/graphify>
- GSD-Pi `main`, release documentation showing v1.20.1, and MIT license, inspected September 27, 2026: <https://github.com/open-gsd/gsd-pi>

No substantial upstream skill or runtime text was copied.

## Planning-document review

| Document | Changed | Reason |
|---|---|---|
| `GlycoLens_00_README.md` | No | Planning-pack navigation and approved direction remain accurate. |
| `GlycoLens_01_Updated_Project_Summary.md` | No | Product scope and model strategy are unchanged. |
| `GlycoLens_02_Model_Inference_and_Dataset_Strategy.md` | No | No model, dataset, or experiment decision changed. |
| `GlycoLens_03_App_Product_Spec_and_UX.md` | No | No user flow or product feature changed. |
| `GlycoLens_04_Tech_Stack_and_System_Architecture.md` | Yes | Added repository and developer-tooling boundaries. |
| `GlycoLens_05_Scientific_Method_and_Evaluation.md` | No | Scientific questions and methods are unchanged. |
| `GlycoLens_06_Milestones_and_Schedule.md` | No | Bootstrap fulfills existing repository-structure work without changing dates or milestones. |
| `GlycoLens_07_Literature_and_Market_Survey.md` | No | No literature or market claim changed. |
| `GlycoLens_08_Risks_Safety_and_Scope.md` | Yes | Clarified that developer Graphify does not reverse the GraphRAG product decision. |
| `GlycoLens_09_Project_Specification_Draft.md` | No | Deliverables and safety boundaries remain accurate. |
