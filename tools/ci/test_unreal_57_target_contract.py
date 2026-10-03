import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04.Target.cs"
EDITOR=ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04Editor.Target.cs"

class Unreal57TargetContractTests(unittest.TestCase):
    def test_project_descriptor_targets_ue57(self):
        project=(ROOT/"unreal"/"NARIS_W04"/"NARIS_W04.uproject").read_text(encoding="utf-8")
        self.assertIn('"EngineAssociation": "5.7"',project)

    def test_ue57_source_api_migrations_are_applied(self):
        public=ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04"/"Public"
        controller=(public/"NarisPlayerController.h").read_text(encoding="utf-8")
        self.assertIn("FInputKeyEventArgs",controller)
        self.assertNotIn("FInputKeyParams",controller)
        for name in ("BoneBeastDataAsset.h","NarisPresentationComponent.h"):
            text=(public/name).read_text(encoding="utf-8")
            self.assertIn('#include "Engine/DataAsset.h"',text)
            self.assertNotIn("Engine/PrimaryDataAsset.h",text)
        shakes=(public/"NarisCameraShakes.h").read_text(encoding="utf-8")
        self.assertIn('#include "Camera/CameraShakeBase.h"',shakes)
        self.assertIn("public UCameraShakeBase",shakes)
        self.assertNotIn("UDefaultCameraShakeBase",shakes)

    def test_camera_shake_modules_are_declared_for_ue57(self):
        build=(ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04"/"NARIS_W04.Build.cs").read_text(encoding="utf-8")
        self.assertIn('"EngineCameras"',build)
        self.assertIn('"GameplayCameras"',build)

    def test_targets_use_ue57_build_settings_and_include_order(self):
        for path in (GAME,EDITOR):
            text=path.read_text(encoding="utf-8")
            self.assertIn("BuildSettingsVersion.V6",text)
            self.assertIn("EngineIncludeOrderVersion.Unreal5_7",text)
            self.assertNotIn("EngineIncludeOrderVersion.Unreal5_4",text)

if __name__=="__main__":
    unittest.main()
