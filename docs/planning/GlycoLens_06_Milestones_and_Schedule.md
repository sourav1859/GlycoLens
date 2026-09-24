# GlycoLens Milestones and Course-Aligned Schedule

## 1. Source-of-truth dates

This plan uses the **current CSCI-788 schedule PDF** for Fall 2026 dates. Older class slides are used only for the **meaning/content of Milestones 1-3**, not for their historical dates.

The course schedule is provisional and the advisor may set earlier deadlines.

### Current course dates

| Item | Current schedule |
|---|---|
| Week 3 - Scientific methods | Sep 8 |
| Project Spec A | Sep 15 |
| Milestone 1 work deadline | **Sep 18** |
| Project Spec B | Sep 22 |
| Milestone 1 A presentation | Sep 29 |
| Milestone 1 B presentation | Oct 6 |
| Milestone 2 work deadline | **Oct 16** |
| Report/poster preparation class | Oct 20 |
| Milestone 2 A | Oct 27 |
| Milestone 2 B | Nov 3 |
| Milestone 3 A | Nov 10 |
| Milestone 3 work deadline | **Nov 13** |
| Milestone 3 B | Nov 17 |
| Poster A | Nov 24 |
| Poster B | Dec 1 |
| Poster final submission | **Dec 6** |
| Final report | **Dec 11** |
| Project defense | **Dec 11, 9:30-11:00 AM** |

## 2. Course meaning of milestones

The course material defines:

### Milestone 1
**Understanding and planning how to solve the problem**
- project specification
- literature review
- current state
- choose and learn methods/tools
- feasibility study
- simulation

### Milestone 2
**Solving the problem**
- algorithms/data structures
- feasibility work
- simulation
- system/code prototyping

### Milestone 3
**Implementing and analyzing the solution**
- system execution
- debugging
- testing
- documentation
- data collection
- verification against specification

The GlycoLens plan below follows this structure.

---

# Milestone 0 - Project Specification
## Sep 7 - Sep 15/22

### Goal
Lock a defensible project scope before heavy development.

### Work

- finalize inference-first scope
- literature survey
- model shortlist:
  - Chronos-2
  - TimesFM-3
  - CGMformer exploratory
- confirm T1D-UOM schema
- download/test public data
- define app MVP
- choose mobile-first PWA
- draft system architecture
- define scientific questions
- define safety boundary
- build repo structure

### Project-spec deliverables

- title
- rationale/problem
- goal
- background
- attack plan
- work plan
- deliverables

### Internal target
Have the project spec substantially ready by **Sep 13**, before the Sep 15 presentation.

---

# Milestone 1 - Understanding, Feasibility, and Planning
## Work deadline: Sep 18
## Presentations: Sep 29 / Oct 6

### Goal
Prove that the proposed architecture is technically feasible.

### Required deliverables

#### Research
- categorized literature survey
- model-selection matrix
- dataset audit
- evaluation protocol

#### Model feasibility
- one Chronos-2 smoke test on CGM
- one TimesFM smoke test if possible
- define common `ForecastModelAdapter`
- verify 2-hour output/quantiles
- record runtime/memory

#### Data
- ingest T1D-UOM
- align at least:
  - CGM
  - meals
  - insulin
- generate first meal-centered windows

#### App/system
- Next.js PWA skeleton
- FastAPI skeleton
- PostgreSQL/Supabase schema
- architecture diagram
- one dummy end-to-end API call

#### Simulation
- py-mgipsim installed and one virtual scenario executed

### Milestone 1 success criteria

- at least one pretrained model runs end to end
- T1D-UOM meal event can be converted into model-ready context
- app can call backend
- scope and model selection criteria are fixed

### What to present

Course presentation guidance suggests:
- problem reminder
- solution reminder
- work completed
- obstacles
- insights
- next milestone
- schedule problems/help needed

---

# Milestone 2 - Solve the Core Problem / Working Prototype
## Work deadline: Oct 16
## Presentations: Oct 27 / Nov 3

### Goal
Have a usable model pipeline and a working application prototype.

### Model/inference deliverables

- Chronos-2 benchmark on core event set
- TimesFM benchmark on same event set
- persistence baseline
- choose top 1-2 models
- context ablation:
  - CGM
  - + insulin
  - + carbs
  - + full nutrition
- first accuracy/latency results

### Data deliverables

- robust T1D-UOM meal-window generator
- leakage checks
- chronological and/or subject-aware test definitions
- data-quality report

### App deliverables

Required screens:
- home CGM timeline
- add meal
- barcode/search
- recipe parser
- nutrition review
- forecast screen

Backend:
- food lookup
- meal save
- forecast endpoint
- model adapter
- timeline endpoint

### Personalization deliverable

- first similar-meal query using SQL + numeric similarity
- pgvector semantic similarity optional but preferred by end of M2

### Integration

At least one:
- Dexcom Sandbox retrieval **or**
- py-mgipsim live scenario inside app

Ideally both by the end of the milestone.

### Milestone 2 success criteria

A user can:

```text
open app
-> choose demo patient
-> enter meal
-> see nutrition
-> run selected pretrained model
-> see forecast
```

---

# Milestone 3 - Integration, Analysis, and Verification
## Work deadline: Nov 13
## Presentations: Nov 10 / Nov 17

Because Milestone 3 A is Nov 10 and the work deadline is Nov 13, aim for an **internal feature freeze by Nov 7**.

### Goal
Turn the prototype into the final evaluated capstone system.

### Required features

- final selected model(s)
- uncertainty visualization
- similar meals / Meal Passport
- what-if portion comparison
- actual-vs-predicted result view
- simulation integration
- Dexcom Sandbox integration if feasible
- error handling/loading states
- provenance labels

### Final analysis

- model comparison
- context ablation
- latency
- uncertainty
- representative forecasts
- limitations

### Testing

- unit tests for data transforms
- model adapter tests
- nutrition calculation tests
- critical Playwright UI flows
- deterministic demo scenario

### Milestone 3 success criteria

- end-to-end app works
- final experiment set is complete or nearly complete
- results are reproducible
- no core feature depends on future development
- demo is reliable offline/local if cloud fails

---

# Poster / Final Stage
## Nov 18 - Dec 11

### Nov 18-23
- freeze main results
- create poster structure
- choose figures

### Nov 24 / Dec 1 poster sessions
- present draft
- collect feedback
- reduce text
- improve visual flow

Course poster guidance emphasizes:
- visual abstract
- readable in about 5 minutes
- title
- introduction
- background
- system/experiment
- results
- conclusions
- references

### By Dec 6
- submit final poster

### Dec 1-10
- final report
- final screenshots
- architecture figure
- results tables
- proofreading
- reproducibility appendix / repo instructions

### Dec 11
- submit report
- defense/demo

---

# 3. Weekly rough plan

| Week | Date | GlycoLens target |
|---|---|---|
| 3 | Sep 8 | Scope + literature + architecture |
| 4 | Sep 15 | Project-spec presentation; model smoke test |
| 5 | Sep 22 | Project-spec refinement; M1 cleanup |
| 6 | Sep 29 | M1 presentation; begin benchmark pipeline |
| 7 | Oct 6 | M1 B; app nutrition flow |
| 8 | Oct 20 | M2 complete; begin full integration |
| 9 | Oct 27 | M2 A; forecast UI + retrieval |
| 10 | Nov 3 | M2 B; complete main features |
| 11 | Nov 10 | M3 A; feature freeze |
| 12 | Nov 17 | M3 B; results freeze |
| 13 | Nov 24 | Poster draft |
| 14 | Dec 1 | Poster final revisions |
| Final | Dec 6-11 | poster/report/defense |

## 4. Scope-cut order if behind

Cut in this order:

1. meal-image recognition
2. GraphRAG/Neo4j
3. real Dexcom users
4. clinician report
5. CGMformer downstream training
6. personal learned calibration
7. activity-context experiment
8. extra model candidates

Do **not** cut:
- working app
- T1D-UOM event pipeline
- at least two pretrained model evaluations
- persistence baseline
- forecast visualization
- meal nutrition
- core results

## 5. Milestone presentation template

Each milestone deck can follow:

1. Problem - 1 slide
2. Current solution/system - 1 slide
3. Previous milestone reminder - 1 slide
4. Progress:
   - completed
   - obstacles
   - insights
5. Results/demo
6. Next milestone
7. Schedule/risks/help needed

The course materials specify a roughly 5-6 minute milestone presentation, so the slides should remain concise.
