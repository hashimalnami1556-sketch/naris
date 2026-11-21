"""Fail-closed numeric analysis of genuine Unreal CSVProfiler files.

This analyzes frame statistics only. It does NOT certify real user gameplay FPS,
a fixed-resolution back buffer, 2-client replication, before/after performance,
GPU budget, or asset quality. Use the UE log to corroborate the capture command.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
from pathlib import Path


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    point = (len(ordered) - 1) * fraction
    lower = math.floor(point)
    upper = math.ceil(point)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (point - lower)


def _metric(values: list[float]) -> dict:
    return {
        "count": len(values),
        "mean": round(statistics.fmean(values), 6),
        "p50": round(_percentile(values, .5), 6),
        "p95": round(_percentile(values, .95), 6),
        "p99": round(_percentile(values, .99), 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def _summary(rows: list[dict[str, float]]) -> dict:
    names = {
        "FrameTime": "frame_time_ms",
        "GameThreadTime": "game_thread_ms",
        "RenderThreadTime": "render_thread_ms",
        "GPUTime": "gpu_time_ms",
        "GPUMem/LocalUsedMB": "gpu_memory_used_mb",
        "GPUMem/LocalBudgetMB": "gpu_memory_budget_mb",
        "MemoryFreeMB": "memory_free_mb",
        "View/Speed2D": "view_speed_2d",
    }
    metrics = {
        label: _metric([r[name] for r in rows if name in r])
        for name, label in names.items()
        if all(name in r for r in rows)
    }
    mean_frame_time = statistics.fmean(r["FrameTime"] for r in rows)
    metrics["fps_from_mean_frame_time"] = round(1000 / mean_frame_time, 6)
    metrics["one_percent_low_fps_from_p99_frame_time"] = round(
        1000 / _percentile([r["FrameTime"] for r in rows], .99), 6
    )
    return metrics


def summarize_csv_text(text: str, *, warmup_frames: int = 60) -> dict:
    """Parse CSVProfiler frame samples, ignoring UE's footer and echoed header.

    Fail instead of reporting a success badge when numeric samples are corrupt.
    Caller decides if the map, viewport, seed and benchmark mode were controlled.
    """
    if not isinstance(warmup_frames, int) or warmup_frames < 0:
        raise ValueError("warmup_frames must be a nonnegative integer")
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    try:
        fields = next(reader)
    except StopIteration as exc:
        raise ValueError("CSVProfiler text empty") from exc
    if "FrameTime" not in fields or "GPUTime" not in fields:
        raise ValueError("CSV must contain FrameTime and GPUTime columns")
    if len(fields) != len(set(fields)):
        raise ValueError("duplicate CSV column names")
    index = {field: col for col, field in enumerate(fields)}
    numeric_fields = [
        f for f in (
            "FrameTime",
            "GPUTime",
            "GameThreadTime",
            "RenderThreadTime",
            "GPUMem/LocalUsedMB",
            "GPUMem/LocalBudgetMB",
            "MemoryFreeMB",
            "View/Speed2D",
        )
        if f in index
    ]
    rows = []
    metadata = {}
    for line_number, raw in enumerate(reader, start=2):
        if not raw or raw == fields:
            continue
        if raw[0].startswith("[HasHeaderRowAtEnd]"):
            for offset in range(2, len(raw) - 1, 2):
                k = raw[offset]
                if k.startswith("[") and k.endswith("]"):
                    metadata[k[1:-1]] = raw[offset + 1]
            continue
        if len(raw) != len(fields):
            raise ValueError(f"CSV frame row {line_number} has {len(raw)} columns, expected {len(fields)}")
        values = {}
        for field in numeric_fields:
            try:
                x = float(raw[index[field]])
            except (ValueError, IndexError) as exc:
                raise ValueError(f"CSV row {line_number} contains nonnumeric {field}") from exc
            if not math.isfinite(x) or (field == "FrameTime" and x <= 0) or (
                field != "FrameTime" and x < 0
            ):
                raise ValueError(f"CSV row {line_number} contains invalid {field}: {x}")
            values[field] = x
        rows.append(values)
    if not rows:
        raise ValueError("no valid measured frame rows")
    if warmup_frames >= len(rows):
        raise ValueError(f"warmup_frames={warmup_frames} leaves no measured frames")
    return {
        "scope": "UE CSV sample statistics only",
        "frame_count": len(rows),
        "warm_frame_count": len(rows) - warmup_frames,
        "warmup_frames": warmup_frames,
        "metadata": metadata,
        "gameplay_fps_certified": False,
        "before_after_delta_certified": False,
        "all": _summary(rows),
        "warm": _summary(rows[warmup_frames:]),
        "limitations": [
            "Benchmark FPS equivalents are derived from recorded FrameTime, not a certified gameplay FPS",
            "UE command flags do not prove physical backbuffer resolution or quality preset",
            "A static developer map cannot represent the final game performance",
            "No before/after performance change is proven without matched paired captures",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect real Unreal CSVProfiler numeric frame samples")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--min-frames", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.min_frames < 1:
        parser.error("--min-frames must be >=1")
    summary = summarize_csv_text(args.csv.read_text(encoding="utf-8-sig"), warmup_frames=args.warmup)
    if summary["frame_count"] < args.min_frames:
        parser.error(f"only {summary['frame_count']} frames; require {args.min_frames}")
    result = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
