# Local LightGBM research option enabled

**November 14, 2026.** The user requested access to the existing LightGBM forecast option in the local UI. It is now enabled in the existing `glycolens-local` runtime: web `http://127.0.0.1:3000`, API port 8000. Chronos remains the default. This is local research/manual-test exposure, not full model/milestone acceptance or production enablement.

## Cause and change

The screenshot's message comes from the authenticated backend capability response. `ForecastModelPicker.tsx` already renders the research option and disables it when the server reports unavailable. The running API had `GLYCOLENS_LIGHTGBM_ENABLED=false`; its approved manifest digest, compatible native dependencies and narrow read-only model mount were already present.

Changed only that flag to true in the ignored root `.env`, verifying that every other parsed setting remained identical and the configured digest matched the existing manifest. Recreated only the current local API with:

```powershell
docker compose --env-file .env up -d --no-deps --wait api
```

The web image/source, model weights, calibration, cloud schema, user meals and source snapshots were not changed by enablement. The shipped `.env.example` still defaults to false. No new cloud fixtures, paid calls, training, calibration or evaluation-cohort access were needed. No commit or push was performed.

## Observed verification

- Before change: the live container reported the flag false, a configured digest and a read-only native mount. A temporary child process with the flag true successfully verified/loaded the existing bundle.
- After API recreation: capabilities returned Chronos available/default with 24 history samples and LightGBM available/nondefault with 288 history samples.
- Real native inference on a handcrafted synthetic request returned **24 points with ordered lower/median/upper endpoints**. No stub model or provider calls were used for this check.
- **13 offline registry/bundle tests passed**, covering default/unknown/unavailable selection, artifact integrity, calibration and signed response contracts. No application source behavior changed, so broader prior regression runs were not repeated.
- Local web and API health both returned HTTP 200. Browser selection/rendering was not directly automated in this work cycle; reload is required because the picker fetches capabilities on mount.

## How to test

1. Reload the current meal page. **LightGBM · research option** should now be selectable.
2. For an eligible forecast, open `/demo` under the same signed-in account, choose the virtual patient, select LightGBM and explicitly start the **48-hour research simulation**.
3. Review food matches/grams and save a **new** meal in that workflow, then run LightGBM. Its source-clock origin has sufficient pre-origin history.

The screenshot's existing meal is attached to the original short one-day source. Enabling a model does not move it to another source or invent additional CGM history; native inference for that source remains rejected. Editing an old meal also does not change its frozen source identity. The common copy composer retains the original meal time, so simply copying it is not sufficient unless its time is deliberately reviewed against the new source. The demo workflow above avoids that ambiguity.

LightGBM uses current carbohydrates, not current protein/fat/fiber, alongside history/event features. Matching-outcome accuracy and interval coverage in this simulation remain unvalidated. The Chronos sensitivity failure and all pending Chrome/manual, failure-variant, presentation and release cases remain recorded. Local exposure does not upgrade `LGB-L4-006` or any other case to PASS.

## Documentation and rollback

Plans 00/01/03/04/06/08/10/17/18, ADR 0022, UI architecture, root/infra guidance, AGENTS and the supplemental ledger now record this local exposure. Scientific protocols, research model choices and acceptance counts are unchanged. Older November 12 off-state reports remain dated historical evidence.

To disable again, set the ignored local flag to false and recreate the API with the same command. Saved owned LightGBM results remain readable; new native requests are rejected, and Chronos remains the default. Artifact trust, history requirements and owner checks are never bypassed.
