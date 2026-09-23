"""Validate W04 production animation assets and native notify contracts.

Missing assets are unresolved work in Development. Set NARIS_ANIMATION_STRICT=1
for Shipping RC, where every required montage must exist and pass validation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import unreal

RELATIVE_MANIFEST = (
    Path("NARIS") / "W04" / "Animation" / "W04_AnimationBindings.json"
)
REPORT_SCHEMA = "naris.w04.animation-validation.v1"


def strict_mode() -> bool:
    return os.environ.get("NARIS_ANIMATION_STRICT", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def notify_class_name(obj) -> str | None:
    if obj is None:
        return None
    try:
        return obj.get_class().get_name()
    except Exception:
        return None


def inspect_notifies(asset) -> tuple[set[str], dict[str, list[float]]]:
    names: set[str] = set()
    durations: dict[str, list[float]] = {}

    for event in unreal.AnimationLibrary.get_animation_notify_events(asset):
        notify = event.get_editor_property("notify")
        state = event.get_editor_property("notify_state_class")

        notify_name = notify_class_name(notify)
        if notify_name:
            names.add(notify_name)

        state_name = notify_class_name(state)
        if state_name:
            names.add(state_name)
            duration = unreal.AnimationLibrary.get_anim_notify_event_duration(event)
            durations.setdefault(state_name, []).append(float(duration))

    return names, durations


def main() -> None:
    content_dir = Path(unreal.Paths.project_content_dir()).resolve()
    manifest_path = content_dir / RELATIVE_MANIFEST

    if not manifest_path.is_file():
        raise RuntimeError(f"Animation binding manifest missing: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "naris.w04.animation-bindings.v1":
        raise RuntimeError("Unsupported W04 animation binding schema")

    validated: list[str] = []
    unresolved: list[str] = []
    errors: list[str] = []
    details: dict[str, dict] = {}

    for item in manifest.get("assets", []):
        asset_id = item.get("asset_id")
        object_path = item.get("expected_unreal_object_path")
        expected_class = item.get("expected_class")
        required = list(item.get("required_notify_classes", []))
        positive_duration = set(item.get("require_positive_state_duration", []))

        if not asset_id or not object_path or expected_class != "AnimMontage":
            errors.append(f"Invalid animation manifest record: {item!r}")
            continue

        if not unreal.EditorAssetLibrary.does_asset_exist(object_path):
            unresolved.append(asset_id)
            continue

        asset = unreal.load_asset(object_path)
        if not isinstance(asset, unreal.AnimMontage):
            errors.append(
                f"{asset_id}: expected AnimMontage at {object_path}, "
                f"got {type(asset).__name__ if asset else 'None'}"
            )
            continue

        notify_names, notify_durations = inspect_notifies(asset)
        missing_notifies = [
            name for name in required if name not in notify_names
        ]
        if missing_notifies:
            errors.append(
                f"{asset_id}: missing required notifies "
                + ", ".join(missing_notifies)
            )
            continue

        bad_state_durations: list[str] = []
        for class_name in positive_duration:
            durations = notify_durations.get(class_name, [])
            if not durations or not any(duration > 0.0 for duration in durations):
                bad_state_durations.append(class_name)

        if bad_state_durations:
            errors.append(
                f"{asset_id}: notify states require positive duration: "
                + ", ".join(bad_state_durations)
            )
            continue

        validated.append(asset_id)
        details[asset_id] = {
            "object_path": object_path,
            "notify_classes": sorted(notify_names),
            "notify_state_durations": {
                name: values
                for name, values in sorted(notify_durations.items())
            },
        }

    status = "fail" if errors or (strict_mode() and unresolved) else "pass"
    report = {
        "schema": REPORT_SCHEMA,
        "status": status,
        "strict": strict_mode(),
        "validated_asset_ids": sorted(set(validated)),
        "unresolved_asset_ids": sorted(set(unresolved)),
        "validated_count": len(set(validated)),
        "unresolved_count": len(set(unresolved)),
        "details": details,
        "errors": errors,
    }

    report_dir = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "naris_animation_validation.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    unreal.log(
        "NARIS_ANIMATION_VALIDATION="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("W04 animation validation found invalid assets")
    if strict_mode() and unresolved:
        raise RuntimeError(
            f"Strict animation validation has {len(set(unresolved))} unresolved assets"
        )


if __name__ == "__main__":
    main()
