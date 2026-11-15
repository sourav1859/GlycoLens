# M2 closure and LightGBM integration test catalog

November 14 contract update: [Plan 19](../planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md) separates personal/current dates from explicit simulation source context. Earlier default-global-source cases/results below are historical where superseded; use the [workspace ledger](workspace-separation-results.json) for the new acceptance contract.

**Version:** 2026-11-12. **Execution:** actual scoped results recorded; combined-layer acceptance remains partial. [Plan 18](../planning/GlycoLens_18_M2_Closure_and_LightGBM_Integration.md) owns scope/dependencies. [Results ledger](m2-closure-lightgbm-results.json) records actual outcomes; this catalog defines acceptance; implemented runners and actual observations are linked in the ledger, and the design alone proves no pass.

Layers: U = offline unit/contract; I = controlled API/database integration; B = Chrome; R = real cached model/simulator; P = bounded real provider; M = human review; V = container/performance. Combined layers require each relevant component. All cases are mandatory for their declared track unless an explicit scoped deferral is recorded. C phases cover original M2 closure; L phases cover additional opt-in integration. A case result cannot automatically promote a mapped legacy case to PASS.

## Fixtures, runners and evidence contract

- Use synthetic owned users A/B, run-tagged disposable cloud records and handcrafted model inputs. Never project consumed primary/PEDAP rows, private CGM exports or identifiable health records into tests.
- Freeze independent expected outputs, feature recipes, versions, model/calibration digests, tolerances and scoring before execution. Review current provider facts against a recorded source/label; keep deterministic offline response fixtures separate from timestamped live facts.
- Every run records command/protocol, run ID, exact source/worktree hashes, image/lockfiles/migrations, model/bundle/features/calibration/scenario identities, environment/target alias, expected/observed values, outcome, evidence and defect. PASS needs actual observations. Failed/blocked attempts and subsequent rechecks remain traceable.
- Evidence below names a **planned sanitized report section** under `docs/reports/m2-closure-validation-<date>.md` (C phases) or `docs/reports/lightgbm-app-validation-<date>.md` (L phases). Raw local logs/rows/traces stay ignored. The reports now exist and contain actual outcomes; see the ledger for each case.
- Implement relevant tests under existing `tests/`, `frontend/` browser/unit runners and `scripts/dev/` integration tooling in the owning phase. L0–L2 should add focused tests for bundle loading, context translation and registry/contracts. L4 should extend the existing container smoke. These additions now exist; real-model/cloud/provider runners require explicit opt-ins, private configuration and reviewed local artifacts.
- Reuse existing regression tests after relevant changes. Real-provider/paid tests need bounded opt-in and remaining total budget. Never reset the hosted database or bulk-delete users. Do not repeat real research training/evaluation as an application integration test.

## C0 — Baseline and prerequisites

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| M2C-C0-001 | U | Record current source/lockfile/migration/model identities; run relevant existing baseline once. | Reproducible revision manifest; actual results separated from earlier checkpoint results and skips. | C0 / baseline |
| M2C-C0-002 | U+I | Value-free private config check; restart API; probe approved cloud/provider readiness without printing settings. | Approved cloud target matches frontend; configured OFF identity loads; no secrets/contact in tracked output; presence alone is not live acceptance. | C0 / readiness |
| M2C-C0-003 | U | Seed prior recipe spend and concurrent requests near total/owner caps; include retry. | Prior USD 0.00763580 and existing reservations count toward USD 5 total; bounded calls stop before allowance is exceeded. | C0 / budget |
| M2C-C0-004 | U+M | Freeze representative fact/extraction oracles and accepted Chrome/camera scope before new provider calls. | Expected answers precede inference; physical-camera cases remain deferred/unpassed; manual barcode and all security gates remain required. | C0 / oracle-manifest |

## C1 — Provider and recipe correctness

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| M2C-C1-001 | U+P | Search/select approved USDA plain food and prepared palak-paneer item; inspect ID, basis, retrieval and attribution. | Chosen item/source identity and per-100g units match source; distinguish similarly named foods rather than treating names as equivalent recipes. | C1 / usda-facts |
| M2C-C1-002 | U | Synthetic per-100g facts 100 kcal, 4g carbs, 5g protein, 7g fat, 1g fiber; scale 250g, yield 2 servings, eat half one serving. | Whole 250g totals 250/10/12.5/17.5/2.5; consumed 62.5/2.5/3.125/4.375/0.625. Rounding only at display. | C1 / scaling-oracle |
| M2C-C1-003 | U | Repeated ingredient, fractional grams, zero nutrient, absent nutrient and cup/piece quantity lacking gram conversion. | Sum repeated grams once per entry; recorded zero remains zero, unknown remains unknown; unsupported household conversion requires confirmation and cannot silently invent grams. | C1 / missingness-units |
| M2C-C1-004 | U+P | Valid known GTIN with live facts, cached repeat and invalid/not-found code; verify OFF request identity/version/volume. | Correct packaged product and nutrient basis; valid contact sent server-side; cached reuse bounded; invalid input makes no provider call; not-found distinct from service error. | C1 / off-contract |
| M2C-C1-005 | U+I | Simulate provider timeout, 429, malformed nutrient, absent carbs and partial database/cache failure. | Bounded retries/backoff; reviewed draft preserved; no invented nutrient zero, fake successful save or leaked provider error/credential; cache/DB partial failure diagnosed. | C1 / degradation |
| M2C-C1-006 | U+P | Frozen representative recipe expected ingredient lists including repeats, nested preparation, ambiguity and malicious instructions; bounded selected-model calls. | Report ingredient recall/precision and quantity/unit/ambiguity correctness against predeclared oracle; schema validity alone cannot count as representative accuracy; no invented nutrient facts. | C1 / recipe-score |
| M2C-C1-007 | U+I | Malformed/oversized/empty model output, unsupported unit and edited match after review; attempt save. | Enforce bounded structured validation, explicit user correction/review and source-backed grams; review invalidated by edits; invalid save atomic and recoverable. | C1 / recipe-validation |
| M2C-C1-008 | U+B | Chrome camera unsupported/denied fixture, then manually enter barcode and navigate away. | Usable manual fallback, no permission loop, stale update or active stream after exit; physical-camera capture is not asserted. | C1 / manual-fallback |

## C2 — Actual app and sensitivity journeys

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| M2C-C2-001 | P+B+I+R | Chrome USDA search -> source/grams review -> save -> real source -> Chronos -> owned persisted reload. | Same reviewed food/portion totals and meal revision in saved forecast snapshot; 24 ordered forecast points and matching owned reload; no mocked live component. | C2 / food-journey |
| M2C-C2-002 | P+B+I+R | Enter a real approved GTIN manually; review label/source/portion; complete save and Chronos forecast. | Product facts/basis persist end to end; correct meal inputs, provenance and result after reload; no physical camera claim. | C2 / barcode-journey |
| M2C-C2-003 | P+B+I+R | Parse approved synthetic recipe, correct ingredient/match/grams, confirm, save, forecast and reload. | Corrections reach source-grounded totals and immutable model snapshot; parser identity and fact sources stay distinct; bounded token/spend evidence recorded. | C2 / recipe-journey |
| M2C-C2-004 | B+I+R | Save/forecast double-click and retry after lost response using stable operation ID; expire/revoke session during subsequent operation. | One durable meal/result per logical operation; no partial forecast; authenticated retry safe, expired/revoked call denied and unsaved state recoverable without unauthorized write. | C2 / retry-auth |
| M2C-C2-005 | I | Owner B attempts owner A meal/result/points/source-context access through actual user API/RLS. | Unauthorized create/read/list denied; no child-point or existence/context disclosure; no privileged admin shortcut used to establish owner access. | C2 / ownership |
| M2C-C2-006 | B+I+R | Save at wall time distinct from fixed simulation; switch source/session; load forecast/history on mobile and desktop. | Virtual origin and wall time labeled separately; no future CGM or cross-session state; old result retains exact frozen context. | C2 / source-time |
| M2C-C2-007 | B+M | Chrome widths 320/390/768/1024/1440/1920; keyboard, 200% zoom, chart table, loading/error/empty states. | Required fields/data/actions readable and reachable; no lost content or page-width overflow; automated and human evidence distinguished from physical-device testing. | C2 / responsive-review |
| M2C-C2-008 | U+R | Execute GL-P09-011 manifest: flat/falling/rising histories, meal profiles, 50/75/100/150/custom portions, 100/250g palak-paneer example, three identical repeats. | Independent input scaling and complete output deltas/repeatability/failures reported; invariant/nonmonotonic response disclosed; preset simulator future not claimed as accuracy truth. | C2 / chronos-sensitivity |

## C3 — Closure and presentation

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| M2C-C3-001 | U+M | Reconcile original M2 phase 5/8/9 requirements with current-revision C evidence and open defects. | Each requirement has actual evidence or named gap; no aggregate pass percentage substitutes for acceptance and no new feature silently expands original M2. | C3 / requirement-map |
| M2C-C3-002 | M | Review current deck/notes model/provider/safety statements against frozen study and app evidence. | Chronos default versus LightGBM research clear; different cohorts not directly compared; poor accuracy/coverage, provider facts and deferred camera disclosed. | C3 / claim-review |
| M2C-C3-003 | M | Presenter opens native v4 PowerPoint, checks layout/hidden backups and rehearses current 7–8 minute notes. | Presenter-recorded native rendering/timing/readability outcome; no screenshot-only or agent-invented rehearsal sign-off. | C3 / presenter-review |
| M2C-C3-004 | U+M | Review final checklist and case ledger with user/presenter; inspect scoped cleanup and private tracked diff. | Declared M2 engineering subset/deferrals explicit; final acceptance decision recorded; no physical camera, email, catalog, hosted or prospective-accuracy pass implied. | C3 / acceptance |

## L0 — Trusted model artifact and parity

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| LGB-L0-001 | U | Valid frozen manifest plus tampered/truncated bundle, bands, feature version or missing file; attempt load. | Full serving manifest validates trusted digests before deserialization; invalid/missing identity disables option without loading or silent fallback. | L0 / artifact-trust |
| LGB-L0-002 | U+R | Load/export trusted winning model in pinned compatible environment; offer client path/module/URL overrides. | Only server-allowlisted artifacts load; dependencies and 31-leaf/24h/events feature recipe verified; no arbitrary pickle, network fetch or research data access. | L0 / loader |
| LGB-L0-003 | U | Hand-specified regular CGM, masks/events/current carbs; compare training translator and serving feature vector. | Exactly 127 origin features in correct order plus horizon fraction in estimator input; equal values/NaN masks and origin-safe timing. | L0 / feature-parity |
| LGB-L0-004 | U+R | Evaluate original trusted in-memory adapter and proposed native serving export on frozen synthetic requests. | 24 medians agree within predeclared 1e-6 mg/dL before rounding; model/version/digest exact; any mismatch blocks export enablement. | L0 / point-parity |
| LGB-L0-005 | U+R | Apply saved lightgbm_direct bands to synthetic point output; tamper participant/coverage/radius dimensions and identity. | 24 ordered symmetric marginal endpoints match point +/- saved radius within 1e-6; saved calibration identity required; invalid bands fail, equal placeholders not accepted as calibrated. | L0 / calibration-parity |
| LGB-L0-006 | U | Trace test inputs/artifact loads and attempt training/refit or reserved-cohort access through serving setup. | No fit/calibration recomputation or reserved outcome projection; synthetic parity only; signed band endpoints retained and synthetic coverage guarantee explicitly absent. | L0 / research-boundary |

## L1 — Longer synthetic context and unit semantics

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| LGB-L1-001 | U+R | Generate separately versioned preferred 48h scenario; select origin after 24h and withhold >=2h future; replay twice. | 288 valid pre-origin samples available, reproducible protocol/hash, future private until clock advance; no padding or unsupported upstream duration bypass. | L1 / long-scenario |
| LGB-L1-002 | U+R | Run original one-day scenario/replay and contract tests alongside new scenario. | Original fixed name/seed/grid/checksums and Chronos path unchanged; each source partition bound to its own protocol. | L1 / old-replay |
| LGB-L1-003 | U | 287/288/289 samples, gaps, off-grid/duplicate/late points and origin boundaries. | Exact 288 regular five-minute model inputs; insufficient/invalid history rejected specifically, never padded or borrowed from future/other source. | L1 / cgm-grid |
| LGB-L1-004 | U | 1.2 U/hour basal for 5min, two rate changes and partial overlaps; 2 U bolus; unknown unit. | First bin basal 0.1 U; 2min at 1.2 plus 3min at 0.6 yields 0.07 U; bolus remains 2 U. Unknown units/coverage fail explicitly. | L1 / insulin-units |
| LGB-L1-005 | U | Confirmed zero bolus/basal/carbs, missing record, absent coverage and recorded glucose; align presence masks. | Binary masks accurately distinguish observed zero, recorded value and unknown; unknown event summaries stay NaN as training recipe requires. | L1 / masks |
| LGB-L1-006 | U | Previous meal, current origin meal, late-available event and future insulin/meal/CGM around five-minute boundaries. | Match training availability/bin rules; current meal counted only in current known-carb feature; future and unavailable late records excluded. | L1 / chronology |
| LGB-L1-007 | U | Same absolute virtual events rendered across timezone/DST display changes and multiple owner/source partitions. | Model features unchanged by display timezone; source/owner isolation preserved; timestamps/availability and deterministic ordering exact. | L1 / source-clock |
| LGB-L1-008 | U+M | Compare simulator insulin/source semantics to training units/masks and document OOD limits. | Numeric conversion independently verified, biological equivalence not assumed; unsupported semantic mapping blocks option rather than labeling source-compatible. | L1 / semantic-review |

## L2 — Registry, transport and persistence

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| LGB-L2-001 | U+I | Omit model, explicitly choose eligible LightGBM, choose unknown name and reuse loaded versions. | Omitted choice resolves Chronos; allowlisted choice resolves full pinned identity; unknown name rejected; cache keys separate bundle/feature/calibration versions. | L2 / registry |
| LGB-L2-002 | U+I | Missing weights/calibration/masks/24h history and busy model; request LightGBM. | Actionable unavailable/insufficient/busy error, bounded lock release and no silent fallback, fake prediction or partial result. | L2 / capabilities |
| LGB-L2-003 | U+I | Ordered finite calibrated interval with q10=-5, median=40, upper=85; old v1 Chronos result; unordered/nonfinite input. | Reviewed v2 API/DB/frontend/export round-trip preserves signed lower endpoint; valid history remains separately constrained; invalid intervals rejected; v1 reads unchanged. | L2 / interval-contract |
| LGB-L2-004 | I | Preview reviewed forward migration against guarded cloud target; exercise ownership/RPC atomic rollback and existing forecast read. | Versioned schema/constraint/RPC change exact and backward compatible; bad request rolls back; no hosted reset. Fresh scratch replay explicitly remains deferred. | L2 / migration |
| LGB-L2-005 | U+I | Retry logical operation with same and changed model/bundle/features/calibration/meal revision. | Same full identity deduplicates; changed identity cannot return stale model result; snapshot includes requested/resolved model, digests, context and scenario protocol. | L2 / idempotency |
| LGB-L2-006 | I | Owner B targets owner A result/points/model snapshot; revoke session and retry. | Verified-owner API/RLS denies access/create; no child/snapshot leakage and no bypass from admin artifact loading. | L2 / ownership |
| LGB-L2-007 | U+I | Run 100% and changed portion through scenarios service, change global default/model request mid-comparison. | Baseline's full frozen model/context identity reused; 100% reproduces within tolerance; cross-model comparison rejected or created as separate labeled experiment. | L2 / scenarios |
| LGB-L2-008 | U+I | Overlapping ordinary/scenario requests, timeout, failure after inference before persistence and retry. | Both paths share intended registry/locking; bounded concurrency, released locks and atomic idempotent persistence; no partial/mixed-model forecast. | L2 / concurrency |

## L3 — Opt-in responsive experience

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| LGB-L3-001 | B+I | New session on current short demo; inspect selector, request opt-in and explicitly start longer scenario. | Chronos default; LightGBM labeled research, 24h requirement actionable; no automatic replacement of current source/scenario. | L3 / selection |
| LGB-L3-002 | B+I | Save LightGBM forecast, reload history/detail, switch owner/source and sign out in another tab. | Persisted result identity survives reload; no cross-owner/source draft/cache leakage; logout clears private selector/context/results. | L3 / identity |
| LGB-L3-003 | B+M | Inspect input explanation and equal-carbohydrate meals differing in fat/protein/fiber. | UI says current carbs are used; nutrition facts remain visible without implying unused predictors affect the frozen model. | L3 / input-explanation |
| LGB-L3-004 | B+M | View calibrated symmetric bands, signed endpoint and unavailable-interval fixture; compare old Chronos chart. | Accurate interval kind/limitations, no unsupported calibration/personal-confidence claim or clipped chart/table data; old quantile wording remains correct. | L3 / intervals |
| LGB-L3-005 | B+M | Chart/detail/table/selector/errors at Chrome 320/390/768/1024/1440/1920, keyboard and zoom. | Critical data/actions accessible without overflow; model, meal/portion and virtual times readable; no physical-device acceptance inferred. | L3 / responsive |
| LGB-L3-006 | B+I | Owned result export and same-model portion comparison; attempt mixed-model comparison from deep link. | Export includes immutable provenance and exact band semantics; same-model comparison coherent; mixed-model route rejected/labeled separately. | L3 / export-comparison |

## L4 — Runtime, sensitivity and enablement

| Case | Layer | Fixture and action | Independent expected result | Evidence section |
|---|---|---|---|---|
| LGB-L4-001 | V+R | Build pinned CPU API image; inspect browser/image/mount boundaries and attempt bundle write. | Compatible LightGBM deps, narrow verified read-only bundle, no research rows/secrets/weights in frontend or tracked files; no GPU/model service required. | L4 / packaging |
| LGB-L4-002 | B+I+R+V | Root Compose actual Chrome -> long scenario -> reviewed save -> opt-in LightGBM -> cloud reload -> portion compare. | 24 ordered persisted points with correct frozen inputs/bands/identity and valid owner access; no stubbed simulator/model/cloud hop. | L4 / complete-journey |
| LGB-L4-003 | R+V | Cold load plus >=20 sequential warm requests/model; record full journey, peak memory, threads, hardware, failures. | Measured median/p95/memory/failure report against predeclared environment-specific limits; no single-run/VPS capacity extrapolation; existing timeouts respected. | L4 / performance |
| LGB-L4-004 | U+R | Frozen LightGBM carbs/portion sensitivity, identical repeats and fat/protein/fiber-only contrasts; same protocol for Chronos. | Carbs reach correct features; repeated same inputs reproducible within tolerance; fat/protein/fiber-only changes leave LightGBM features/predictions unchanged; flat/nonmonotonic results disclosed without accuracy claim. | L4 / sensitivity |
| LGB-L4-005 | B+I+R+V | Disable opt-in, restart API, corrupt optional bundle and reopen saved results; run relevant Chronos/demo/replay/logout regressions. | Chronos default continues; explicit LightGBM readiness error; historical owned results readable; no data deletion or automatic fallback. | L4 / rollback-regression |
| LGB-L4-006 | U+M | Review all mandatory L cases, defects, data/secret boundaries, limitations and prospective-accuracy status before enablement. | Enable only after relevant correctness/security/integration evidence passes; consumed cohorts untouched; GL-P09-012 remains separate; no automatic default promotion. | L4 / enablement |

## Legacy traceability and future work

| Requirement | New cases | Existing contract references |
|---|---|---|
| Provider-grounded meal entry and confirmation | C1, C2-001/002/003 | GL-P04-001/002/005/006/007/008 |
| Durable meal and immutable forecast | C2-004/005/006, L2 | GL-P04-011/012; GL-P05-001/003/006/008/009 |
| Responsive accessibility and honest source UI | C2-007, L3 | GL-P02-001/002/003/004/009 |
| Sensitivity versus genuine outcome accuracy | C2-008, L4-004/006 | GL-P09-011; GL-P09-012 remains separate and unexecuted |
| Physical camera and real-device denial behavior | No new physical test in this scope | GL-P04-003/004: NOT_RUN, scope_disposition DEFERRED_BY_USER; browser fallback remains tested in C1-008 |
| Versioned schema, owner isolation, readiness and recovery | L2, L4 | GL-P01-001/003/006/007; GL-P10-005/006/007/012 |

Short references such as C2-001 above mean `M2C-C2-001`; phase labels refer to every case in that phase. Future physical-camera tests require a real approved device/browser/HTTPS setup. Separate prospective accuracy, corrected catalog, SMTP, scratch restore and hosting require their own prerequisites and acceptance; these tests cannot waive them.
