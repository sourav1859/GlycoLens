from scripts.dev.summarize_meal_response import summarize


def test_numerical_noise_is_not_counted_as_meal_response_capability():
    report = dict(
        status="PASS",
        models={m: dict(identical_repeat_max_error_mg_dl=0) for m in ("chronos", "lightgbm")},
        rows=[
            dict(model="chronos", portion=0.5, max_endpoint_delta_mg_dl=0.00000763),
            dict(model="lightgbm", portion=0.5, max_endpoint_delta_mg_dl=3),
            dict(model="lightgbm", single_nutrient="fat_g", max_endpoint_delta_mg_dl=0),
        ],
    )
    scored = summarize(report)
    assert scored["engineering_checks"] == "PASS"
    assert scored["models"]["chronos"]["status"] == "FAIL_INVARIANT"
    assert scored["models"]["lightgbm"]["eligible_contrasts"] == 1
    assert scored["accuracy_status"] == "NOT_VALIDATED" and not scored["all_phase_gates_passed"]


def test_missing_comparisons_never_pass_a_gate():
    scored = summarize(dict(status="PASS", models={}, rows=[]))
    assert all(v["status"] == "NOT_EVALUATED" for v in scored["models"].values())
