"""Create/update W04 material instances from the canonical material bindings.

This script intentionally does NOT fabricate M_MASTER_SURFACE or M_MASTER_WATER.
Those masters are authored Technical-Art assets. Once they exist, this script
creates or updates the ten deterministic W04 MaterialInstanceConstant assets and
applies the exact scalar/vector values from W04_MaterialBindings.json.

NARIS_MATERIALS_STRICT=1 makes missing master materials a hard failure.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import unreal

BINDINGS_RELATIVE = (
    Path("NARIS") / "W04" / "Materials" / "W04_MaterialBindings.json"
)
REPORT_SCHEMA = "naris.w04.material-authoring.v1"


def strict_mode() -> bool:
    return os.environ.get("NARIS_MATERIALS_STRICT", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def load_asset_required(path: str):
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return None
    return unreal.load_asset(path)


def ensure_instance(asset_tools, object_path: str):
    if unreal.EditorAssetLibrary.does_asset_exist(object_path):
        instance = unreal.load_asset(object_path)
        if not isinstance(instance, unreal.MaterialInstanceConstant):
            raise RuntimeError(
                f"Expected MaterialInstanceConstant at {object_path}"
            )
        return instance, "updated"

    package_path, object_name = object_path.rsplit("/", 1)
    asset_name = object_name.split(".", 1)[0]
    factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = asset_tools.create_asset(
        asset_name=asset_name,
        package_path=package_path,
        asset_class=unreal.MaterialInstanceConstant,
        factory=factory,
    )
    if instance is None:
        raise RuntimeError(f"Could not create material instance: {object_path}")
    return instance, "created"


def set_scalar(instance, name: str, value: float) -> None:
    ok = unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
        instance,
        unreal.Name(name),
        float(value),
    )
    if not ok:
        raise RuntimeError(
            f"Parent does not expose scalar parameter {name!r}"
        )


def set_vector(instance, name: str, value: list[float]) -> None:
    values = list(value)
    while len(values) < 4:
        values.append(1.0)
    color = unreal.LinearColor(
        float(values[0]),
        float(values[1]),
        float(values[2]),
        float(values[3]),
    )
    ok = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
        instance,
        unreal.Name(name),
        color,
    )
    if not ok:
        raise RuntimeError(
            f"Parent does not expose vector parameter {name!r}"
        )


def main() -> None:
    bindings_path = Path(unreal.Paths.project_content_dir()) / BINDINGS_RELATIVE
    if not bindings_path.is_file():
        raise RuntimeError(f"Material bindings missing: {bindings_path}")

    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    if bindings.get("schema") != "naris.w04.material-bindings.v1":
        raise RuntimeError("Unsupported W04 material binding schema")

    masters: dict[str, object] = {}
    unresolved_master_paths: list[str] = []
    errors: list[str] = []

    for profile, path in bindings.get("masters", {}).items():
        master = load_asset_required(path)
        if master is None:
            unresolved_master_paths.append(path)
            continue
        if not isinstance(master, unreal.Material):
            errors.append(f"{profile}: expected base Material at {path}")
            continue
        masters[profile] = master

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    authored: list[str] = []
    skipped: list[str] = []
    statuses: dict[str, str] = {}

    for item in bindings.get("assets", []):
        asset_id = item["asset_id"]
        profile = item["profile"]
        master = masters.get(profile)
        if master is None:
            skipped.append(asset_id)
            continue

        try:
            instance, status = ensure_instance(
                asset_tools,
                item["expected_unreal_object_path"],
            )
            unreal.MaterialEditingLibrary.set_material_instance_parent(
                instance,
                master,
            )

            for name, value in (
                item.get("parameters", {}).get("scalar", {}).items()
            ):
                set_scalar(instance, name, value)

            for name, value in (
                item.get("parameters", {}).get("vector", {}).items()
            ):
                set_vector(instance, name, value)

            unreal.MaterialEditingLibrary.update_material_instance(instance)
            statuses[asset_id] = status
            authored.append(asset_id)
        except Exception as exc:
            errors.append(f"{asset_id}: {exc}")

    if authored:
        unreal.EditorAssetLibrary.save_directory(
            "/Game/NARIS/W04/Materials",
            only_if_is_dirty=False,
            recursive=True,
        )

    status = "fail" if errors else "pass"
    if strict_mode() and (unresolved_master_paths or skipped):
        status = "fail"

    report = {
        "schema": REPORT_SCHEMA,
        "status": status,
        "strict": strict_mode(),
        "authored_asset_ids": sorted(set(authored)),
        "skipped_asset_ids": sorted(set(skipped)),
        "unresolved_master_paths": sorted(set(unresolved_master_paths)),
        "asset_status": statuses,
        "errors": errors,
    }

    out = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "naris_material_authoring.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    unreal.log(
        "NARIS_MATERIAL_AUTHORING="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("W04 material instance authoring found errors")
    if strict_mode() and (unresolved_master_paths or skipped):
        raise RuntimeError(
            "Strict material authoring has unresolved master/material work"
        )


if __name__ == "__main__":
    main()
