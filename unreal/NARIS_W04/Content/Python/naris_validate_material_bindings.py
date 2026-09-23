"""Validate W04 material instances against the authored material library.

Development reports missing masters/instances as unresolved production work.
NARIS_MATERIALS_STRICT=1 turns unresolved material work into a Shipping blocker.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import unreal

BINDINGS_RELATIVE = (
    Path("NARIS") / "W04" / "Materials" / "W04_MaterialBindings.json"
)
TOLERANCE = 0.02


def strict_mode() -> bool:
    return os.environ.get("NARIS_MATERIALS_STRICT", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def repo_root() -> Path:
    return Path(unreal.Paths.project_dir()).resolve().parents[1]


def close_enough(actual: float, expected: float) -> bool:
    return abs(float(actual) - float(expected)) <= TOLERANCE


def main() -> None:
    bindings_path = Path(unreal.Paths.project_content_dir()) / BINDINGS_RELATIVE
    if not bindings_path.is_file():
        raise RuntimeError(f"Material bindings missing: {bindings_path}")

    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    if bindings.get("schema") != "naris.w04.material-bindings.v1":
        raise RuntimeError("Unsupported W04 material binding schema")

    root = repo_root()
    registry = json.loads(
        (root / "data" / "MASTER_ASSET_REGISTRY.json").read_text(encoding="utf-8")
    )
    library = json.loads(
        (root / bindings["library"]).read_text(encoding="utf-8")
    )

    registry_ids = {
        item.get("id")
        for item in registry.get("assets", [])
        if isinstance(item, dict)
    }
    library_ids = {
        item.get("id")
        for item in library.get("materials", [])
        if isinstance(item, dict)
    }
    library_ids.add(library["water"]["id"])

    unresolved_master_paths: list[str] = []
    master_details: dict[str, dict] = {}
    errors: list[str] = []

    for profile, requirement in bindings.get("master_requirements", {}).items():
        path = requirement.get("path")
        if not path or not unreal.EditorAssetLibrary.does_asset_exist(path):
            if path:
                unresolved_master_paths.append(path)
            continue

        master = unreal.load_asset(path)
        if not isinstance(master, unreal.Material):
            errors.append(f"{profile}: expected base Material at {path}")
            continue

        scalar_names = {
            str(name)
            for name in unreal.MaterialEditingLibrary.get_scalar_parameter_names(master)
        }
        vector_names = {
            str(name)
            for name in unreal.MaterialEditingLibrary.get_vector_parameter_names(master)
        }

        required_scalars = set(requirement.get("scalar_parameters", []))
        required_vectors = set(requirement.get("vector_parameters", []))
        missing_scalars = sorted(required_scalars - scalar_names)
        missing_vectors = sorted(required_vectors - vector_names)

        expected_blend_name = requirement.get("blend_mode")
        expected_blend = getattr(unreal.BlendMode, expected_blend_name, None)
        actual_blend = master.get_blend_mode()

        if expected_blend is None:
            errors.append(
                f"{profile}: unsupported expected blend mode {expected_blend_name!r}"
            )
        elif actual_blend != expected_blend:
            errors.append(
                f"{profile}: blend mode {actual_blend} != {expected_blend}"
            )

        if missing_scalars:
            errors.append(
                f"{profile}: master missing scalar parameters "
                + ", ".join(missing_scalars)
            )
        if missing_vectors:
            errors.append(
                f"{profile}: master missing vector parameters "
                + ", ".join(missing_vectors)
            )

        master_details[profile] = {
            "path": path,
            "blend_mode": str(actual_blend),
            "scalar_parameters": sorted(scalar_names),
            "vector_parameters": sorted(vector_names),
            "missing_scalar_parameters": missing_scalars,
            "missing_vector_parameters": missing_vectors,
        }

    unresolved_asset_ids: list[str] = []
    validated_asset_ids: list[str] = []
    details: dict[str, dict] = {}

    for item in bindings.get("assets", []):
        asset_id = item.get("asset_id")
        library_id = item.get("material_library_id")
        object_path = item.get("expected_unreal_object_path")
        expected_parent = item.get("expected_parent")

        if asset_id not in registry_ids:
            errors.append(f"{asset_id}: missing from MASTER_ASSET_REGISTRY")
            continue
        if library_id not in library_ids:
            errors.append(f"{asset_id}: unknown material library id {library_id}")
            continue
        if item.get("expected_class") != "MaterialInstanceConstant":
            errors.append(f"{asset_id}: unsupported expected material class")
            continue

        if not unreal.EditorAssetLibrary.does_asset_exist(object_path):
            unresolved_asset_ids.append(asset_id)
            continue

        instance = unreal.load_asset(object_path)
        if not isinstance(instance, unreal.MaterialInstanceConstant):
            errors.append(
                f"{asset_id}: expected MaterialInstanceConstant at {object_path}"
            )
            continue

        parent = instance.get_editor_property("parent")
        parent_path = parent.get_path_name() if parent is not None else ""
        if parent_path != expected_parent:
            errors.append(
                f"{asset_id}: parent mismatch {parent_path!r} != {expected_parent!r}"
            )
            continue

        scalar_actual: dict[str, float] = {}
        vector_actual: dict[str, list[float]] = {}
        parameter_errors: list[str] = []

        for name, expected in item.get("parameters", {}).get("scalar", {}).items():
            try:
                actual = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(
                    instance,
                    unreal.Name(name),
                )
                scalar_actual[name] = float(actual)
                if not close_enough(actual, expected):
                    parameter_errors.append(
                        f"{name}={float(actual):.4f} expected {float(expected):.4f}"
                    )
            except Exception as exc:
                parameter_errors.append(f"{name}: {exc}")

        for name, expected in item.get("parameters", {}).get("vector", {}).items():
            try:
                actual = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(
                    instance,
                    unreal.Name(name),
                )
                values = [
                    float(actual.r),
                    float(actual.g),
                    float(actual.b),
                    float(actual.a),
                ]
                vector_actual[name] = values
                expected_values = list(expected)
                while len(expected_values) < 4:
                    expected_values.append(1.0)
                if any(
                    not close_enough(a, e)
                    for a, e in zip(values, expected_values[:4])
                ):
                    parameter_errors.append(
                        f"{name}={values!r} expected {expected_values[:4]!r}"
                    )
            except Exception as exc:
                parameter_errors.append(f"{name}: {exc}")

        if parameter_errors:
            errors.append(
                f"{asset_id}: material parameters do not match library: "
                + "; ".join(parameter_errors)
            )
            continue

        validated_asset_ids.append(asset_id)
        details[asset_id] = {
            "object_path": object_path,
            "parent_path": parent_path,
            "scalar_parameters": scalar_actual,
            "vector_parameters": vector_actual,
        }

    status = "fail" if errors else "pass"
    if strict_mode() and (unresolved_master_paths or unresolved_asset_ids):
        status = "fail"

    report = {
        "schema": "naris.w04.material-validation.v1",
        "status": status,
        "strict": strict_mode(),
        "validated_asset_ids": sorted(set(validated_asset_ids)),
        "unresolved_asset_ids": sorted(set(unresolved_asset_ids)),
        "unresolved_master_paths": sorted(set(unresolved_master_paths)),
        "master_details": master_details,
        "details": details,
        "errors": errors,
    }

    out = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "naris_material_validation.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    unreal.log(
        "NARIS_MATERIAL_VALIDATION="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )

    if errors:
        raise RuntimeError("W04 material validation found invalid materials")
    if strict_mode() and (unresolved_master_paths or unresolved_asset_ids):
        raise RuntimeError(
            "Strict material validation has unresolved masters/material instances"
        )


if __name__ == "__main__":
    main()
