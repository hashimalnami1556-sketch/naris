"""ANIM-024: verify expected W04 montage catalog against checked-in project files."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"/"assetforge"))
from anim024_repo_readiness import evaluate_repo_assets, asset_to_file

def fixture():
    return {"schema":"naris.w04.animation-bindings.v1","assets":[
      {"asset_id":"C-1","role":"hero_light_attack","expected_unreal_object_path":
       "/Game/NARIS/W04/Characters/Hero/Animations/AM_Hero_LightAttack.AM_Hero_LightAttack",
       "expected_class":"AnimMontage","required_notify_classes":["NarisAttackImpactNotify"]},
      {"asset_id":"C-2","role":"hero_dodge","expected_unreal_object_path":
       "/Game/NARIS/W04/Characters/Hero/Animations/AM_Hero_Dodge.AM_Hero_Dodge",
       "expected_class":"AnimMontage","required_notify_classes":[]}
    ]}

class RepoReadiness(unittest.TestCase):
    def test_unavailable_montages_are_not_certified(self):
        with tempfile.TemporaryDirectory() as d:
            r=evaluate_repo_assets(fixture(),Path(d))
        self.assertEqual(r["missing_checked_in_uassets"],2)
        self.assertFalse(r["production_ready"])
    def test_present_binary_still_not_UE_runtime_verified(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            dest=asset_to_file(root,fixture()["assets"][0]["expected_unreal_object_path"])
            dest.parent.mkdir(parents=True);dest.write_bytes(b"fake-not-a-real-uasset")
            r=evaluate_repo_assets(fixture(),root)
        self.assertEqual(r["present_file_candidates"],1)
        self.assertFalse(r["production_ready"])
    def test_manifest_rejects_duplicate_role(self):
        m=fixture();m["assets"][1]["role"]="hero_light_attack"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):evaluate_repo_assets(m,Path(td))
    def test_unexpected_class_is_blocked(self):
        m=fixture();m["assets"][0]["expected_class"]="StaticMesh"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):evaluate_repo_assets(m,Path(td))
    def test_block_path_traversal(self):
        with self.assertRaises(ValueError):
            asset_to_file(Path("/tmp/game"),"/Game/../Secrets.Key")
    def test_block_outside_game(self):
        with self.assertRaises(ValueError):
            asset_to_file(Path("/tmp/game"),"/Engine/Test.Test")
    def test_invalid_schema_rejected(self):
        m=fixture();m["schema"]="anything else"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):evaluate_repo_assets(m,Path(td))
    def test_actual_w04_manifest_is_not_auto_certified(self):
        repo=Path(__file__).resolve().parents[2]
        path=repo/"unreal/NARIS_W04/Content/NARIS/W04/Animation/W04_AnimationBindings.json"
        if not path.is_file():self.skipTest("W04 manifest absent from this checkout")
        m=json.loads(path.read_text())
        r=evaluate_repo_assets(m,repo/"unreal/NARIS_W04/Content")
        self.assertEqual(r["expected_anim_montages"],10)
        self.assertFalse(r["production_ready"])
if __name__=="__main__":unittest.main()
