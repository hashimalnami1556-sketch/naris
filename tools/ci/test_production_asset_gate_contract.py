from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"unreal/NARIS_W04/Content/NARIS/W04/Production/W04_ProductionAssetBindings.json"

def read(rel): return (ROOT/rel).read_text(encoding="utf-8")

class ProductionAssetGateContractTests(unittest.TestCase):
    def test_core_manifest_is_registry_backed(self):
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        r=json.loads(read("data/MASTER_ASSET_REGISTRY.json"))
        ids={x.get("id") for x in r.get("assets",[]) if isinstance(x,dict)}
        self.assertEqual(m["schema"],"naris.w04.production-assets.v1")
        self.assertEqual(len(m["assets"]),7)
        for item in m["assets"]:
            self.assertIn(item["asset_id"],ids)
            self.assertTrue(item["expected_unreal_object_path"].startswith("/Game/NARIS/W04/"))
            self.assertGreaterEqual(item["min_lods"],2)

    def test_skeletal_requirements_are_explicit(self):
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        sk=[x for x in m["assets"] if x["kind"]=="skeletal_mesh"]
        self.assertEqual(len(sk),3)
        for item in sk:
            self.assertTrue(item["require_materials"])
            self.assertTrue(item["require_skeleton"])
            self.assertTrue(item["require_physics_asset"])
            self.assertGreaterEqual(item["min_lods"],3)

    def test_static_requirements_are_explicit(self):
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        sm=[x for x in m["assets"] if x["kind"]=="static_mesh"]
        self.assertEqual(len(sm),4)
        for item in sm:
            self.assertTrue(item["require_materials"])
            self.assertTrue(item["require_collision"])

    def test_unreal_validator_checks_real_engine_properties(self):
        s=read("unreal/NARIS_W04/Content/Python/naris_validate_production_assets.py")
        for token in ("StaticMeshEditorSubsystem","SkeletalMeshEditorSubsystem","get_lod_count","get_num_lods","physics_asset","skeleton","static_materials","customized_collision","get_convex_collision_count","NARIS_PRODUCTION_ASSETS_STRICT","naris_production_asset_validation.json"):
            self.assertIn(token,s)

if __name__=="__main__": unittest.main()
