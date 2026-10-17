"""The fixed origin-known C2 request used by the MetaboNet correction study."""

from dataclasses import replace


def c2_request(request):
    if len(request.target_history) < 72:
        raise ValueError("frozen C2 requires at least six hours of glucose")
    names = {
        "insulin_bolus",
        "insulin_basal",
        "insulin_bolus_record_present",
        "insulin_basal_record_present",
        "cgm_record_present",
        "previous_meal_carbohydrates",
        "previous_meal_carbohydrates_record_present",
    }
    return replace(
        request,
        target_history=request.target_history[-72:],
        past_covariates=tuple(
            replace(s, points=s.points[-72:]) if s.name == "cgm_record_present" else s
            for s in request.past_covariates
            if s.name in names
        ),
        known_covariates=tuple(
            s for s in request.known_covariates if s.name == "meal_carbohydrates"
        ),
    )
