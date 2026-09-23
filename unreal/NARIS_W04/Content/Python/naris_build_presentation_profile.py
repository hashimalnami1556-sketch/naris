"""Build/update the shared W04 presentation profile from source manifests.

This runs inside Unreal Editor after the NARIS_W04 C++ module has compiled.
Null binding paths are explicit unbound presentation work, not fabricated assets.

Environment:
  NARIS_PRESENTATION_STRICT=1  -> fail if any referenced payload is unbound.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import unreal

RELATIVE_DIR = Path("NARIS") / "W04" / "Presentation"
MANIFEST_FILE = "W04_PresentationCueManifest.json"
BINDINGS_FILE = "W04_PresentationAssetBindings.json"
REPORT_SCHEMA = "naris.w04.presentation-authoring.v1"


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise RuntimeError(f"Required presentation source is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def strict_mode() -> bool:
    return os.environ.get("NARIS_PRESENTATION_STRICT", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def ensure_profile(asset_tools, profile_path: str):
    if unreal.EditorAssetLibrary.does_asset_exist(profile_path):
        profile = unreal.load_asset(profile_path)
        if profile is None:
            raise RuntimeError(f"Could not load presentation profile: {profile_path}")
        return profile, "loaded"

    profile_class = getattr(unreal, "NarisPresentationProfile", None)
    if profile_class is None:
        raise RuntimeError(
            "NarisPresentationProfile is unavailable. Build the C++ module first."
        )

    package_path, asset_name = profile_path.rsplit("/", 1)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", profile_class)
    profile = asset_tools.create_asset(
        asset_name=asset_name,
        package_path=package_path,
        asset_class=profile_class,
        factory=factory,
    )
    if profile is None:
        raise RuntimeError(f"Could not create presentation profile: {profile_path}")
    return profile, "created"


def load_binding(binding: dict, kind: str, errors: list[str]):
    object_path = binding.get("unreal_object_path")
    if not object_path:
        return None

    try:
        if kind == "camera":
            loaded = unreal.load_class(None, object_path)
            if loaded is None:
                errors.append(
                    f"Camera class could not be loaded: {binding['asset_id']} -> {object_path}"
                )
            return loaded

        loaded = unreal.load_asset(object_path)
        if loaded is None:
            errors.append(
                f"Asset could not be loaded: {binding['asset_id']} -> {object_path}"
            )
            return None

        if kind == "vfx":
            if not isinstance(loaded, unreal.NiagaraSystem):
                errors.append(
                    f"Expected NiagaraSystem for {binding['asset_id']}, "
                    f"got {type(loaded).__name__}"
                )
                return None

            validator = getattr(
                unreal,
                "NarisPresentationValidationLibrary",
                None,
            )
            if validator is None:
                errors.append(
                    "NarisPresentationValidationLibrary is unavailable"
                )
                return None

            if not validator.is_niagara_system_non_empty(loaded):
                errors.append(
                    f"NiagaraSystem has no emitters: {binding['asset_id']}"
                )
                return None

        if kind == "audio" and not isinstance(loaded, unreal.SoundBase):
            errors.append(
                f"Expected SoundBase for {binding['asset_id']}, got {type(loaded).__name__}"
            )
            return None

        return loaded
    except Exception as exc:
        errors.append(f"Failed loading {binding['asset_id']}: {exc}")
        return None


def resolve_audio_bus(value: str):
    enum_class = getattr(unreal, "NarisPresentationAudioBus", None)
    if enum_class is None:
        raise RuntimeError(
            "NarisPresentationAudioBus is unavailable. Build the C++ module first."
        )

    mapping = {
        "sfx": "SFX",
        "music": "MUSIC",
        "voice": "VOICE",
    }
    enum_name = mapping.get((value or "").strip().lower())
    if not enum_name:
        raise ValueError(f"Unsupported presentation audio bus: {value!r}")

    resolved = getattr(enum_class, enum_name, None)
    if resolved is None:
        raise RuntimeError(
            f"NarisPresentationAudioBus has no reflected value {enum_name}"
        )
    return resolved


def collect_runtime_cues(manifest: dict) -> list[dict]:
    cues = list(manifest.get("cues", []))
    for dynamic in manifest.get("dynamic_cues", []):
        runtime_cue = dynamic.get("runtime_cue")
        if not runtime_cue:
            continue
        entry = {"cue": runtime_cue}
        for key in ("vfx", "audio", "camera", "audio_bus"):
            if dynamic.get(key):
                entry[key] = dynamic[key]
        cues.append(entry)
    return cues


def main() -> None:
    content_dir = Path(unreal.Paths.project_content_dir())
    source_dir = content_dir / RELATIVE_DIR
    manifest = load_json(source_dir / MANIFEST_FILE)
    bindings = load_json(source_dir / BINDINGS_FILE)

    if manifest.get("schema") != "naris.w04.presentation-cues.v1":
        raise RuntimeError("Unsupported presentation cue manifest schema")
    if bindings.get("schema") not in {
        "naris.w04.presentation-bindings.v1",
        "naris.w04.presentation-bindings.v2",
    }:
        raise RuntimeError("Unsupported presentation binding schema")

    profile_path = bindings.get(
        "profile_asset",
        "/Game/NARIS/W04/Presentation/DA_W04_Presentation",
    )

    binding_by_id = {
        item["asset_id"]: item
        for item in bindings.get("assets", [])
        if isinstance(item, dict) and item.get("asset_id")
    }

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    profile, profile_status = ensure_profile(asset_tools, profile_path)

    cue_struct_class = getattr(unreal, "NarisPresentationCue", None)
    if cue_struct_class is None:
        raise RuntimeError("NarisPresentationCue struct is unavailable")

    errors: list[str] = []
    unbound: list[str] = []
    unbound_expected_paths: dict[str, str] = {}
    bound: list[str] = []
    cue_structs = []

    for cue_def in collect_runtime_cues(manifest):
        cue_id = cue_def.get("cue")
        if not cue_id:
            errors.append("Presentation cue entry is missing cue id")
            continue

        cue = cue_struct_class()
        cue.set_editor_property("cue_id", unreal.Name(cue_id))

        audio_asset_id = cue_def.get("audio")
        audio_bus_value = cue_def.get("audio_bus")
        if audio_asset_id:
            if not audio_bus_value:
                errors.append(
                    f"Presentation cue {cue_id} has audio but no audio_bus"
                )
            else:
                try:
                    cue.set_editor_property(
                        "audio_bus",
                        resolve_audio_bus(audio_bus_value),
                    )
                except Exception as exc:
                    errors.append(
                        f"Presentation cue {cue_id} has invalid audio_bus: {exc}"
                    )
        elif audio_bus_value:
            errors.append(
                f"Presentation cue {cue_id} declares audio_bus without audio"
            )

        for source_key, property_name, kind in (
            ("vfx", "niagara_system", "vfx"),
            ("audio", "sound", "audio"),
            ("camera", "camera_shake", "camera"),
        ):
            asset_id = cue_def.get(source_key)
            if not asset_id:
                continue

            binding = binding_by_id.get(asset_id)
            if binding is None:
                errors.append(f"No binding record for {asset_id}")
                continue

            if binding.get("kind") != kind:
                errors.append(
                    f"Binding kind mismatch for {asset_id}: "
                    f"{binding.get('kind')!r} != {kind!r}"
                )
                continue

            if not binding.get("unreal_object_path"):
                unbound.append(asset_id)
                expected_path = binding.get("expected_unreal_object_path")
                if expected_path:
                    unbound_expected_paths[asset_id] = expected_path
                continue

            loaded = load_binding(binding, kind, errors)
            if loaded is not None:
                cue.set_editor_property(property_name, loaded)
                bound.append(asset_id)

        cue_structs.append(cue)

    profile.set_editor_property("cues", cue_structs)

    package_dir = profile_path.rsplit("/", 1)[0]
    if not unreal.EditorAssetLibrary.save_directory(
        package_dir,
        only_if_is_dirty=False,
        recursive=True,
    ):
        raise RuntimeError(f"Could not save presentation profile directory: {package_dir}")

    report = {
        "schema": REPORT_SCHEMA,
        "status": "fail" if errors or (strict_mode() and unbound) else "pass",
        "strict": strict_mode(),
        "profile_asset": profile_path,
        "profile_status": profile_status,
        "cue_count": len(cue_structs),
        "bound_asset_ids": sorted(set(bound)),
        "unbound_asset_ids": sorted(set(unbound)),
        "unbound_expected_paths": {
            asset_id: unbound_expected_paths[asset_id]
            for asset_id in sorted(unbound_expected_paths)
        },
        "errors": errors,
    }

    report_dir = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "naris_presentation_authoring.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    unreal.log(
        "NARIS_PRESENTATION_AUTHORING_RESULT="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("Presentation authoring has invalid bindings")
    if strict_mode() and unbound:
        raise RuntimeError(
            f"Strict presentation authoring has {len(set(unbound))} unbound asset IDs"
        )


if __name__ == "__main__":
    main()
