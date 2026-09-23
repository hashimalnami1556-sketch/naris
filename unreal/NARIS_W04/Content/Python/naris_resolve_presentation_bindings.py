"""Resolve real W04 presentation payloads at deterministic Unreal paths.

Runs inside Unreal Editor. It never creates VFX/audio/camera payloads and never
marks an asset bound unless Unreal can load the expected object with the correct
type. Camera native /Script bindings already present in the binding file are
validated but not fabricated.

Environment:
  NARIS_PRESENTATION_STRICT=1 -> unresolved required payloads make this script fail.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import unreal

RELATIVE_DIR = Path("NARIS") / "W04" / "Presentation"
BINDINGS_FILE = "W04_PresentationAssetBindings.json"
REPORT_SCHEMA = "naris.w04.presentation-binding-resolution.v1"


def strict_mode() -> bool:
    return os.environ.get("NARIS_PRESENTATION_STRICT", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def load_candidate(item: dict, object_path: str, errors: list[str]):
    kind = item.get("kind")
    asset_id = item.get("asset_id", "<unknown>")

    try:
        if kind == "camera":
            loaded = unreal.load_class(None, object_path)
            if loaded is None:
                return None
            return loaded

        loaded = unreal.load_asset(object_path)
        if loaded is None:
            return None

        if kind == "audio" and not isinstance(loaded, unreal.SoundBase):
            errors.append(
                f"{asset_id}: expected SoundBase at {object_path}, "
                f"got {type(loaded).__name__}"
            )
            return None

        if kind == "vfx" and not isinstance(loaded, unreal.NiagaraSystem):
            errors.append(
                f"{asset_id}: expected NiagaraSystem at {object_path}, "
                f"got {type(loaded).__name__}"
            )
            return None

        return loaded
    except Exception as exc:
        errors.append(f"{asset_id}: failed loading {object_path}: {exc}")
        return None


def main() -> None:
    source_dir = Path(unreal.Paths.project_content_dir()) / RELATIVE_DIR
    bindings_path = source_dir / BINDINGS_FILE

    if not bindings_path.is_file():
        raise RuntimeError(f"Presentation binding file missing: {bindings_path}")

    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    if bindings.get("schema") != "naris.w04.presentation-bindings.v2":
        raise RuntimeError("Presentation binding resolver requires bindings v2")

    resolved: list[str] = []
    already_bound: list[str] = []
    unresolved: list[str] = []
    errors: list[str] = []

    for item in bindings.get("assets", []):
        if not isinstance(item, dict):
            errors.append("Binding list contains a non-object item")
            continue

        asset_id = item.get("asset_id")
        expected = item.get("expected_unreal_object_path")
        actual = item.get("unreal_object_path")

        if not asset_id or not expected:
            errors.append(f"Binding missing asset_id/expected path: {item!r}")
            continue

        if actual:
            if load_candidate(item, actual, errors) is not None:
                already_bound.append(asset_id)
            else:
                errors.append(
                    f"{asset_id}: declared binding is not loadable: {actual}"
                )
            continue

        loaded = load_candidate(item, expected, errors)
        if loaded is None:
            unresolved.append(asset_id)
            continue

        item["unreal_object_path"] = expected
        item["binding_source"] = "resolved_expected_path"
        resolved.append(asset_id)

    bindings_path.write_text(
        json.dumps(bindings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = {
        "schema": REPORT_SCHEMA,
        "status": "fail"
        if errors or (strict_mode() and unresolved)
        else "pass",
        "strict": strict_mode(),
        "resolved_asset_ids": sorted(set(resolved)),
        "already_bound_asset_ids": sorted(set(already_bound)),
        "unresolved_asset_ids": sorted(set(unresolved)),
        "resolved_count": len(set(resolved)),
        "already_bound_count": len(set(already_bound)),
        "unresolved_count": len(set(unresolved)),
        "errors": errors,
    }

    report_dir = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "naris_presentation_binding_resolution.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    unreal.log(
        "NARIS_PRESENTATION_BINDING_RESOLUTION="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("Presentation binding resolution found invalid payloads")
    if strict_mode() and unresolved:
        raise RuntimeError(
            f"Strict binding resolution has {len(set(unresolved))} unresolved assets"
        )


if __name__ == "__main__":
    main()
