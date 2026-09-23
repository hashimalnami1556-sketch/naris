"""Validate and import real W04 presentation WAV masters into Unreal.

Missing source files are explicitly skipped. Invalid files fail the import pass.
No audio is generated or fabricated by this script.
"""
from __future__ import annotations

import json
import wave
from pathlib import Path

import unreal

PLAN_RELATIVE = Path("NARIS") / "W04" / "Presentation" / "W04_PresentationSourcePlan.json"
REPORT_SCHEMA = "naris.w04.presentation-audio-import.v1"


def validate_wav(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    info: dict = {}

    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            compression = wav.getcomptype()
    except Exception as exc:
        return info, [f"{path}: unreadable WAV: {exc}"]

    duration = frames / sample_rate if sample_rate > 0 else 0.0
    info = {
        "channels": channels,
        "sample_width_bytes": sample_width,
        "sample_rate_hz": sample_rate,
        "frames": frames,
        "duration_seconds": round(duration, 6),
        "compression": compression,
    }

    if sample_rate != 48000:
        errors.append(f"{path}: expected 48000 Hz, got {sample_rate}")
    if sample_width != 3:
        errors.append(
            f"{path}: expected 24-bit PCM (3-byte samples), got {sample_width * 8}-bit"
        )
    if channels not in (1, 2):
        errors.append(f"{path}: expected 1 or 2 channels, got {channels}")
    if compression != "NONE":
        errors.append(f"{path}: expected uncompressed PCM, got {compression}")
    if duration <= 0.0:
        errors.append(f"{path}: audio duration must be positive")
    if duration > 30.0:
        errors.append(f"{path}: presentation one-shot exceeds 30 seconds")

    return info, errors


def parse_expected_path(expected: str) -> tuple[str, str]:
    if not expected.startswith("/Game/") or "." not in expected:
        raise ValueError(f"Expected Unreal asset path is invalid: {expected}")

    destination_path, object_name = expected.rsplit("/", 1)
    asset_name = object_name.split(".", 1)[0]
    return destination_path, asset_name


def main() -> None:
    project_dir = Path(unreal.Paths.project_dir()).resolve()
    repo_root = project_dir.parent.parent
    plan_path = Path(unreal.Paths.project_content_dir()).resolve() / PLAN_RELATIVE

    if not plan_path.is_file():
        raise RuntimeError(f"Presentation source plan missing: {plan_path}")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema") != "naris.w04.presentation-source-plan.v1":
        raise RuntimeError("Unsupported presentation source plan schema")

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    imported: list[str] = []
    already_present: list[str] = []
    skipped_missing: list[str] = []
    errors: list[str] = []
    wav_info: dict[str, dict] = {}

    for item in plan.get("assets", []):
        if not isinstance(item, dict) or item.get("kind") != "audio":
            continue

        asset_id = item.get("asset_id")
        source_rel = item.get("source_file")
        expected = item.get("expected_unreal_object_path")

        if not asset_id or not source_rel or not expected:
            errors.append(f"Audio plan item is incomplete: {item!r}")
            continue

        source_path = (repo_root / source_rel).resolve()

        if unreal.EditorAssetLibrary.does_asset_exist(expected):
            loaded = unreal.load_asset(expected)
            if isinstance(loaded, unreal.SoundBase):
                already_present.append(asset_id)
                continue
            errors.append(
                f"{asset_id}: target exists but is not SoundBase: {expected}"
            )
            continue

        if not source_path.is_file():
            skipped_missing.append(asset_id)
            continue

        info, source_errors = validate_wav(source_path)
        wav_info[asset_id] = info
        if source_errors:
            errors.extend(source_errors)
            continue

        destination_path, destination_name = parse_expected_path(expected)

        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(source_path))
        task.set_editor_property("destination_path", destination_path)
        task.set_editor_property("destination_name", destination_name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("replace_existing_settings", False)
        task.set_editor_property("save", True)

        asset_tools.import_asset_tasks([task])
        objects = list(task.get_objects())
        sound = next(
            (obj for obj in objects if isinstance(obj, unreal.SoundBase)),
            None,
        )

        if sound is None:
            errors.append(f"{asset_id}: WAV import produced no SoundBase")
            continue

        actual_path = sound.get_path_name()
        if actual_path != expected:
            errors.append(
                f"{asset_id}: imported path mismatch: {actual_path} != {expected}"
            )
            continue

        unreal.EditorAssetLibrary.set_metadata_tag(
            sound,
            unreal.Name("NARIS.AssetId"),
            asset_id,
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            sound,
            unreal.Name("NARIS.SourceFile"),
            str(source_path),
        )
        imported.append(asset_id)

    report = {
        "schema": REPORT_SCHEMA,
        "status": "fail" if errors else "pass",
        "imported_asset_ids": sorted(set(imported)),
        "already_present_asset_ids": sorted(set(already_present)),
        "skipped_missing_asset_ids": sorted(set(skipped_missing)),
        "wav_info": wav_info,
        "errors": errors,
    }

    report_dir = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "naris_presentation_audio_import.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    unreal.log(
        "NARIS_PRESENTATION_AUDIO_IMPORT="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("Presentation audio import failed validation")


if __name__ == "__main__":
    main()
