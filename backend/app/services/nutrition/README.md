# Nutrition Service

Own USDA FoodData Central and Open Food Facts adapters, deterministic nutrition calculations, provenance, caching, and safe fallback behavior.

`providers.py` normalizes explicit per-100-g facts, retains missing nutrients as unknown,
and restricts catalog writes to fetched provider facts. SQL calculates saved serving totals
and snapshots the source values. `recipes.py` uses strict structured Responses extraction
of ingredients/quantities only, with model/key supplied privately and retention disabled.
The user confirms/edit ingredients and grams before database-grounded nutrition is saved.
Live USDA/recipe checks await configuration; synthetic fixtures are not provider evidence.
