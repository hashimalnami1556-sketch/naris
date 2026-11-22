"""Review04 offline source-and-asset gate: does NOT substitute for Unreal engine validation."""
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(r"C:\Users\Admin\NARIS")
GIS=ROOT/"Saved/GIS/Jeddah"
V4=GIS/"LEVEL001_AlBalad_Footprints_Review04"
class Review04AssetGate(unittest.TestCase):
    def test_v4_integrity_and_provenance(self):
        m=json.loads((V4/"JED_AlBalad_ArchitecturalDetails_V4_manifest.json").read_text())
        path=V4/"JED_AlBalad_ArchitecturalDetails_V4.glb"
        raw=path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),m["glb_sha256"])
        self.assertEqual(raw[:4],b"glTF")
        self.assertEqual(struct.unpack_from("<I",raw,8)[0],len(raw))
        self.assertEqual((m["source_buildings_selected"],m["decorated_buildings"]),(189,189))
        self.assertEqual(m["max_outward_projection_m"],.3)
        self.assertEqual(m["license"],"ODbL 1.0")
        self.assertFalse(m["production_approved"])
    def test_three_materials_and_three_meshes(self):
        raw=(V4/"JED_AlBalad_ArchitecturalDetails_V4.glb").read_bytes()
        n=struct.unpack_from("<I",raw,12)[0];d=json.loads(raw[20:20+n])
        self.assertEqual(len(d["materials"]),3)
        self.assertEqual(len(d["meshes"]),3)
        self.assertTrue(all(len(v["primitives"])==1 for v in d["meshes"]))
        self.assertEqual(sum(d["accessors"][p["indices"]]["count"]//3 for m in d["meshes"]
                             for p in m["primitives"]),140784)
        self.assertFalse("images" in d)
        self.assertFalse(d["asset"]["extras"]["historical_accuracy_verified"])
    def test_review_only_unreal_installer_has_protective_gate(self):
        s=(GIS/"LEVEL001_import_art_review04_UE57.py").read_text()
        for token in ("30*(1024**3)","NARIS_LEVEL001_REVIEW_IMPORT_APPROVE",
                      "duplicate_asset(OLD_MAP,NEW_MAP)","LEVEL001_CANONICAL_OR_REVIEW03_MODIFIED",
                      "production_approved","collision_tested","navigation_tested"):
            self.assertIn(token,s)
        self.assertNotIn("delete_asset(",s)
        self.assertNotIn("replace_existing\":True",s)
    def test_rendered_blender_evidence_is_not_falsely_ue(self):
        report=json.loads((V4/"LEVEL001_V4_BlenderPreview_Report.json").read_text())
        self.assertEqual(report["renderer"],"BLENDER_WORKBENCH")
        self.assertFalse(report["render_is_unreal"])
        for name in ("before_gis_v3_overview.png","after_detail_v4_overview.png",
                     "after_detail_v4_street_perspective.png"):
            self.assertGreater((V4/"Preview"/name).stat().st_size,200000)
        self.assertFalse(report["production_approved"])
if __name__=="__main__":unittest.main(verbosity=2)
