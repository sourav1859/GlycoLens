"""Prepare/clean a tagged synthetic account for opt-in localhost browser acceptance.

Never prints the disposable password or JWT. Uses the existing exact cloud guard.
"""

import argparse
from datetime import datetime, timezone
import json
from uuid import uuid4
from scripts.dev.cloud_preflight import ROOT, read_configuration, new_run_id
from scripts.dev.workspace_integration import WorkspaceHarness

FIXTURE = ROOT / ".cache/workspace-browser-fixture.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    if not args.allow_cloud:
        raise SystemExit("Explicit --allow-cloud required; no requests dispatched")
    run_id = json.loads(FIXTURE.read_text())["run_id"] if args.cleanup else new_run_id()
    h = WorkspaceHarness(read_configuration(), allow_cloud=True, run_id=run_id)
    with h.bounded_network():
        if args.cleanup:
            h.cleanup()
            FIXTURE.unlink(missing_ok=True)
            print(json.dumps(dict(cleanup_completed=h.manifest["cleanup_completed"])))
            return
        try:
            a = h.create_user("browser")
            me = h.api(a, "POST", "/me/bootstrap", {})
            for step, values in [
                ("preferences", dict(timezone="America/New_York", glucose_unit="mg/dL")),
                ("source", dict(source_mode="personal")),
                ("optional", dict(display_name="Synthetic browser reviewer")),
            ]:
                me = h.api(
                    a,
                    "PATCH",
                    "/me/onboarding",
                    dict(step=step, revision=me["onboarding"]["revision"], values=values),
                )
            h.api(
                a,
                "POST",
                "/me/onboarding/complete",
                dict(
                    revision=me["onboarding"]["revision"],
                    notice_version="research-v1",
                    acknowledged=True,
                ),
            )
            food_id = str(uuid4())
            h.manifest["foods"].append(food_id)
            h.save_manifest()
            assert (
                h.request(
                    "POST",
                    "/rest/v1/foods",
                    admin=True,
                    body=dict(
                        id=food_id,
                        name="Synthetic browser food",
                        source="synthetic_test",
                        source_food_id=run_id,
                        nutrient_basis_g=100,
                        calories=180,
                        carbs_g=30,
                        protein_g=8,
                        fat_g=4,
                        fiber_g=5,
                    ),
                ).status_code
                == 201
            )
            now = datetime.now(timezone.utc).isoformat()
            body = dict(
                workspace="personal",
                name="Personal browser acceptance meal",
                recorded_at=now,
                consumed_at=now,
                state="logged",
                confirmed=True,
                idempotency_key=str(uuid4()),
                items=[dict(food_id=food_id, grams=100)],
            )
            h.api(a, "POST", "/meals", body)
            source = h.api(
                a, "POST", "/simulation/scenario", dict(replay=True, protocol="m1_fixed_meal_day")
            )
            h.api(
                a,
                "POST",
                "/meals",
                {
                    **body,
                    "workspace": "simulation",
                    "source_session_id": source["source_session_id"],
                    "name": "Earlier browser virtual meal",
                    "recorded_at": source["forecast_origin"],
                    "state": "planned",
                    "consumed_at": None,
                    "idempotency_key": str(uuid4()),
                },
            )
            # A controlled browser test may read only this ignored disposable fixture.
            FIXTURE.write_text(
                json.dumps(
                    dict(
                        run_id=run_id,
                        project_ref=h.run.project_ref,
                        email=a["email"],
                        password=a["password"],
                    )
                ),
                encoding="utf-8",
            )
            print(
                json.dumps(dict(prepared=True, synthetic_users=1, paid_calls=0, email_messages=0))
            )
        except BaseException:
            h.cleanup()
            raise


if __name__ == "__main__":
    main()
