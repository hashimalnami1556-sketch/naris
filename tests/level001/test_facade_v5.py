"""LEVEL-001 V5 projected rawashin tests: require authentic OSM geometry, no UE claims."""
import hashlib,json,struct,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'/'level001'))
import LEVEL001_facade_v5 as v5

class ProjectedRawashinV5Tests(unittest.TestCase):
    def data(self,path):
        src={"origin_wgs84":{"lat":21.4839,"lon":39.1875},
             "source":"OpenStreetMap contributors","license":"ODbL 1.0",
             "buildings":[
              {"osm_id":101,"height_m":12.6,"footprint_cm":[[0,0],[1100,0],[1100,800],[0,800],[0,0]]},
              {"osm_id":102,"height_m":10.1,"footprint_cm":[[3000,0],[4200,0],[4200,900],[3000,900],[3000,0]]},
              {"osm_id":103,"height_m":8.1,"footprint_cm":[[700000,0],[701100,0],[701100,800],[700000,800],[700000,0]]}],
             "roads":[{"osm_id":44,"class":"pedestrian","points_cm":[[-150,-200],[4500,-200]]}]}
        path.write_text(json.dumps(src),encoding="utf-8")
    def test_oriel_is_actually_projected_and_proportional(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);self.data(p/"in.json")
            r=v5.export_projected_rawashin(p/"in.json",p/"review")
            self.assertEqual(r["eligible_building_count"],2)
            self.assertEqual(r["decorated_building_count"],2)
            self.assertGreaterEqual(r["projected_rawashin_count"],2)
            self.assertGreaterEqual(r["lattice_rails_count"],24)
            self.assertGreaterEqual(r["max_outward_projection_m"],.70)
            self.assertLessEqual(r["max_outward_projection_m"],1.0)
            self.assertGreater(r["triangle_count"],300)
    def test_deterministic_binary_and_exact_license(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=p/"in.json";self.data(src)
            digest=hashlib.sha256(src.read_bytes()).hexdigest()
            one=v5.export_projected_rawashin(src,p/"a")
            two=v5.export_projected_rawashin(src,p/"b")
            self.assertEqual(one["glb_sha256"],two["glb_sha256"])
            self.assertEqual(one["source_sha256"],digest)
            self.assertEqual(one["license"],"ODbL 1.0")
            self.assertFalse(one["photomatch_verified"])
            self.assertFalse(one["production_approved"])
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),digest)
            with self.assertRaises(FileExistsError):v5.export_projected_rawashin(src,p/"a")
    def test_glb_is_valid_with_materials_and_no_external_images(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);self.data(p/"in.json")
            v5.export_projected_rawashin(p/"in.json",p/"a")
            b=(p/"a/JED_AlBalad_ProjectedRawashin_V5.glb").read_bytes()
            self.assertEqual(b[:4],b"glTF")
            self.assertEqual(struct.unpack_from("<I",b,8)[0],len(b))
            n=struct.unpack_from("<I",b,12)[0]
            doc=json.loads(b[20:20+n])
            self.assertEqual(len(doc["meshes"]),3)
            self.assertEqual(len(doc["materials"]),3)
            self.assertNotIn("images",doc)
            self.assertNotIn("extensionsUsed",doc)
            self.assertFalse(doc["asset"]["extras"]["historical_accuracy_verified"])
    def test_too_small_or_unlicensed_footprints_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);self.data(p/"in.json")
            d=json.loads((p/"in.json").read_text())
            d["license"]="UNKNOWN"
            (p/"in.json").write_text(json.dumps(d))
            with self.assertRaises(ValueError):v5.export_projected_rawashin(p/"in.json",p/"bad")
            d["license"]="ODbL 1.0";d["buildings"]=[]
            (p/"in.json").write_text(json.dumps(d))
            with self.assertRaises(ValueError):v5.export_projected_rawashin(p/"in.json",p/"empty")
if __name__=="__main__":unittest.main(verbosity=2)
