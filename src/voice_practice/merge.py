"""60/30 windowing and the final runner's silence-aware hybrid join."""

import math
from .transcripts import Row


def review_starts(duration: float, window: float = 60.0, step: float = 30.0) -> list[float]:
    if any(not math.isfinite(x) or x <= 0 for x in (duration, window, step)) or step > window:
        raise ValueError("Duration/window/step must be positive and finite, with step <= window")
    starts = [0.0]
    # Multiplication avoids cumulative fractional-step drift.
    while starts[-1] + window < duration:
        starts.append(len(starts) * step)
    return starts


def choose_seam(left: list[Row], right: list[Row], overlap_start: float,
                overlap_len: float, silences: list[tuple[float, float]],
                max_edge_error: float = 1.6) -> dict:
    if overlap_len <= 0:
        return {"seam": overlap_start, "method": "no_overlap", "overlap_start": overlap_start, "overlap_len": overlap_len}
    center = overlap_start + overlap_len / 2.0
    candidates = []
    for first, last in silences:
        seam = (first + last) / 2.0
        if not overlap_start <= seam <= overlap_start + overlap_len:
            continue
        left_kept = [row for row in left if row.midpoint < seam]
        right_kept = [row for row in right if row.midpoint >= seam]
        if not left_kept or not right_kept:
            continue
        left_edge = max(left_kept, key=lambda row: row.end)
        right_edge = min(right_kept, key=lambda row: row.start)
        candidates.append({
            "seam": seam, "silence_start": first, "silence_end": last,
            "silence_duration": last - first,
            "edge_error": abs(left_edge.end - first) + abs(right_edge.start - last),
            "center_distance": abs(seam - center),
            "left_boundary": {"from": left_edge.start, "to": left_edge.end, "text": left_edge.text},
            "right_boundary": {"from": right_edge.start, "to": right_edge.end, "text": right_edge.text},
        })
    base = {"overlap_start": overlap_start, "overlap_len": overlap_len}
    safe = [item for item in candidates if item["edge_error"] <= max_edge_error]
    if safe:
        best = min(safe, key=lambda item: (-item["silence_duration"], item["edge_error"], item["center_distance"]))
        method = "hybrid_safe"
    elif candidates:
        best = min(candidates, key=lambda item: (item["edge_error"], item["center_distance"], -item["silence_duration"]))
        method = "fallback_min_edge"
    else:
        return {**base, "seam": center, "method": "fallback_center_no_silence"}
    return {**base, **{key: value for key, value in best.items() if key != "center_distance"}, "method": method}


def merge_windows(windows: list[list[Row]], seams: list[dict]) -> list[Row]:
    if len(seams) != max(0, len(windows) - 1):
        raise ValueError("Each adjacent window pair requires exactly one seam")
    positions = [item["seam"] for item in seams]
    if positions != sorted(positions):
        raise ValueError("Seams must be ordered")
    merged = []
    for index, rows in enumerate(windows):
        low = positions[index - 1] if index else None
        high = positions[index] if index < len(positions) else None
        merged.extend(row for row in rows if (low is None or row.midpoint >= low) and (high is None or row.midpoint < high))
    return sorted(merged, key=lambda row: (row.start, row.window_start if row.window_start is not None else -1.0))
