# Retrieval Service

Own same-user similar-meal retrieval using PostgreSQL, pgvector, and transparent numeric similarity. Graphify is not a product retrieval dependency.
M2 implementation: `numeric.py` ranks same-owner SQL candidates by fixed-scale macro
distance (carbs/50, protein/25, fat/20, fiber/10). Missing macros are not treated as zero.
SQL requires an earlier meal and an outcome available by the query origin. The first
prototype displays simulator-derived outcomes with explicitly illustrative nutrition;
it does not modify model physiology. Semantic embeddings remain optional later work.
