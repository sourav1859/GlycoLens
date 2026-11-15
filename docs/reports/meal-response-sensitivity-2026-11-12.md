# Application meal and portion sensitivity results

**Result: GL-P09-011 meal-response capability FAIL for Chronos; limited synthetic carbohydrate sensitivity for opt-in LightGBM.** Correct input plumbing and repeatability passed. Matching-outcome accuracy (GL-P09-012) remains NOT_RUN. This is a synthetic diagnostic, not new cohort evaluation or patient guidance.

## Frozen protocol and execution

The preexisting [protocol](../testing/meal-response-validation-protocol.md) predeclared 0.001 mg/dL numerical indistinguishability. Manifest `config/meal-response-validation.json`, SHA256 `12b2a166c24f32d6174b41c216881fb12010b1e32ba42859e4e23e9b2a407945`, froze flat/falling/rising histories, lower/higher carbohydrate, fat/protein and fiber profiles, 50/75/100/150/custom portions, illustrative palak-paneer 100/250g and three repeated identical baselines. All nutrition values are labeled synthetic; no catalog recipe was validated by these fixtures.

The Linux CPU run completed **236/236 predictions (118 per model)**, including 20 sequential warm benchmarks/model, all 24 ordered finite forecast endpoints and captured inputs. Each model produced 72 contrast/control rows. The independent scorer excludes controls and features unused by that model from its changed-input denominator. Exact repeated inputs produced zero endpoint spread. The driver also recorded a stricter pre-run 1e-6 repeat/flat diagnostic; the primary published capability classification uses the earlier **0.001**, without changing inputs, weights or thresholds after results.

| Primary sensitivity observation | Chronos C3 | LightGBM |
|---|---:|---:|
| Eligible changed-input contrasts | 60 | 51 |
| Indistinguishable at 0.001 mg/dL | 60 (100%) | 6 (11.76%) |
| Largest absolute endpoint change, mg/dL | 0.0000076294 | 13.9066 |
| Illustrative palak-paneer 100g -> 250g max endpoint change, mg/dL | 0 | 2.9193 |
| Identical-repeat maximum spread, mg/dL | 0 | 0 |
| Capability disposition | **FAIL_INVARIANT** | LIMITED_SYNTHETIC_SENSITIVITY |

Chronos received the approved changed carbohydrate/protein/fat/fiber covariate channels, yet its outputs were effectively invariant at the declared tolerance. The original raw runner's `PASS` described engineering matrix completion; it must not be interpreted as a passed capability gate. `summarize_meal_response.py` independently classifies these saved outputs; the updated runner now includes that classification and returns an overall partial disposition when capability fails. No expensive re-inference was needed to correct the interpretation.

LightGBM receives current carbohydrates only. Equal-carbohydrate fat/protein/fiber contrasts correctly produce unchanged features/predictions and do not count as eligible changed-input contrasts. Its nonzero carbohydrate responses show that this frozen model can change its output, but do not establish correct direction, useful magnitude, reliable portion relationships, physiological equivalence, accuracy or causality. Flat and nonmonotonic outputs remain visible; there is no monotonic-response acceptance rule.

## Consequences

Chronos remains default under the user's approved decision. Its result notice/help disclose the failed synthetic meal-response capability; no automatic model switch, nutrition encoding change, retuning or recalibration follows. Native LightGBM remains an explicitly chosen, gated research option. Protein/fat/fiber are nutrition facts rather than direct inputs to that candidate.

The simulator's later preset meals are not replaced by the user's proposed meal, so its future CGM cannot establish accuracy for that arbitrary meal. Primary/PEDAP test cohorts were already consumed; none were reopened, refit or relabeled independent. A new prospectively approved source/protocol with genuinely matching meals, portions and later observations is needed for GL-P09-012. M2/P09 are not fully accepted by this diagnostic.

Detailed generated inputs/outputs remain in ignored artifacts. Reproduction uses `scripts/dev/validate_meal_response.py` with its explicit real-model opt-in and `scripts/dev/summarize_meal_response.py` on the saved output. No cloud writes, paid calls, new training or reserved-cohort rows were used.
