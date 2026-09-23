from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLAN = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationSourcePlan.json"
)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationVFXValidationContractTests(unittest.TestCase):
    def test_source_plan_has_fourteen_required_vfx_payloads(self) -> None:
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        vfx = [
            item
            for item in plan.get("assets", [])
            if item.get("kind") == "vfx"
        ]
        self.assertEqual(len(vfx), 14)
        for item in vfx:
            self.assertEqual(item.get("status"), "required")
            self.assertEqual(
                item["source_contract"]["unreal_class"],
                "NiagaraSystem",
            )
            self.assertIn(
                "/Game/NARIS/W04/Presentation/VFX/",
                item["expected_unreal_object_path"],
            )

    def test_native_validator_rejects_empty_niagara_system(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/"
            "NarisPresentationValidationLibrary.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisPresentationValidationLibrary.cpp"
        )
        self.assertIn("IsNiagaraSystemNonEmpty", header)
        self.assertIn("System->GetEmitterHandles().Num() > 0", source)

    def test_binding_resolver_uses_native_niagara_validator(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_resolve_presentation_bindings.py"
        )
        self.assertIn("NarisPresentationValidationLibrary", source)
        self.assertIn("is_niagara_system_non_empty", source)
        self.assertIn("NiagaraSystem has no emitter handles", source)

    def test_profile_authoring_uses_native_niagara_validator(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_build_presentation_profile.py"
        )
        self.assertIn("NarisPresentationValidationLibrary", source)
        self.assertIn("is_niagara_system_non_empty", source)
        self.assertIn("NiagaraSystem has no emitters", source)

    def test_empty_vfx_cannot_satisfy_strict_shipping_gate(self) -> None:
        resolver = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_resolve_presentation_bindings.py"
        )
        rc = read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn("errors.append(", resolver)
        self.assertIn(
            "$Presentation.errors).Count -ne 0",
            rc,
        )


if __name__ == "__main__":
    unittest.main()
