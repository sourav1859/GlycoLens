"""SQL candidate filtering and transparent nutrient-distance ranking."""

from math import sqrt
from uuid import UUID

from fastapi import HTTPException

from backend.app.db.client import UserSession, database_call


def similar_meals(session: UserSession, meal_id: UUID):
    meals = database_call(session, f"meals?id=eq.{meal_id}&select=*")
    if not meals:
        raise HTTPException(404, "Meal not found")
    meal = meals[0]
    # RPC filters same owner, strictly earlier meals, and completed outcomes.
    candidates = database_call(
        session, "rpc/similar_meal_candidates", method="POST", payload={"p_meal": str(meal_id)}
    )
    fields = (("carbs_g", 50), ("protein_g", 25), ("fat_g", 20), ("fiber_g", 10))
    ranked = []
    for candidate in candidates:
        if any(meal.get(field) is None or candidate.get(field) is None for field, _ in fields):
            continue
        distance = sqrt(
            sum(
                ((float(meal[field]) - float(candidate[field])) / scale) ** 2
                for field, scale in fields
            )
        )
        ranked.append(
            {
                **candidate,
                "similarity": 1 / (1 + distance),
                "method": "numeric_macro_distance_v1",
                "source": "simulated_history",
            }
        )
    return sorted(ranked, key=lambda row: (-row["similarity"], row["id"]))[:5]
