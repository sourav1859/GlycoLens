"""Paired participant-cluster intervals; CGM points are never independent samples."""

import random
import statistics
from collections import defaultdict


def paired_participant_interval(
    left: list[dict], right: list[dict], *, seed=20261014, samples=2000
):
    left_rows = {row["event_id"]: row for row in left if not row["error_type"]}
    right_rows = {row["event_id"]: row for row in right if not row["error_type"]}
    groups = defaultdict(list)
    for event in sorted(left_rows.keys() & right_rows.keys()):
        if left_rows[event]["participant_id"] != right_rows[event]["participant_id"]:
            raise ValueError("paired events must refer to the same participant")
        groups[left_rows[event]["participant_id"]].append(
            left_rows[event]["metrics"]["mae"] - right_rows[event]["metrics"]["mae"]
        )
    means = [statistics.mean(values) for values in groups.values()]
    if not means:
        raise ValueError("no matched participant events")
    rng = random.Random(seed)
    draws = sorted(statistics.mean(rng.choices(means, k=len(means))) for _ in range(samples))
    return {
        "participant_count": len(means),
        "matched_events": len(left_rows.keys() & right_rows.keys()),
        "macro_mae_difference": statistics.mean(means),
        "bootstrap_95_low": draws[int(samples * 0.025)],
        "bootstrap_95_high": draws[int(samples * 0.975)],
        "method": "paired_participant_cluster_percentile",
        "seed": seed,
        "samples": samples,
    }
