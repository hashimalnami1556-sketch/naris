"""LEVEL-001 facade preview: behavior tests. RED first; no Unreal engine claims."""
import hashlib, json, struct, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'/'level001'))
import LEVEL001_facade_v4 as art

class FacadeV4Tests(unittest.TestCase):
    def fixture(self,path):
        d={
           "origin_wgs84":{"lat":21.4839,"lon":39.1875},
           "source":"OpenStreetMap contributors",
           "license":"ODbL 1.0",
           "buildings":[
             {"osm_id":101,"height_m":9.6,"footprint_cm":[[0,0],[1100,0],[1100,800],[0,800],[0,0]]},
             {"osm_id":102,"height_m":12.4,"footprint_cm":[[3000,0],[4300,0],[4300,700],[3000,700]]},
             {"osm_id":103,"height_m":9.6,"footprint_cm":[[500000,500000],[501000,500000],[501000,501000],[500000,501000]]}
           ],
           "roads":[{"osm_id":44,"class":"pedestrian","points_cm":[[-100, -550],[5000,-550]]}]
        }
        path.write_text(json.dumps(d),encoding="utf-8")
    def test_axes_point_outwards_for_ccw_ring(self):
        tang, norm=art.wall_axes((0,0),(1100,0))
        self.assertAlmostEqual(tang[0],1,places=5)
        self.assertAlmostEqual(norm[2],1,places=5)
        self.assertAlmostEqual(sum(x*x for x in norm),1,places=5)
    def test_creates_review_glb_and_selects_real_source_ids(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/"fixture.json";self.fixture(source)
            before=hashlib.sha256(source.read_bytes()).hexdigest()
            report=art.build_facades(source,p/"out",21.4839,39.1875,500)
            out=p/"out/JED_AlBalad_ArchitecturalDetails_V4.glb"
            self.assertEqual(report["source_buildings_selected"],2)
            self.assertGreater(report["decorated_buildings"],0)
            self.assertTrue(set(report["decorated_osm_ids"]).issubset({101,102}))
            self.assertEqual(report["license"],"ODbL 1.0")
            self.assertEqual(struct.unpack_from("<I",out.read_bytes(),8)[0],out.stat().st_size)
            self.assertFalse(report["production_approved"])
            self.assertFalse(report["photomatch_approved"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
    def test_refuses_overwrite_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/"fixture.json";self.fixture(source)
            first=art.build_facades(source,p/"v4a")
            second=art.build_facades(source,p/"v4b")
            self.assertEqual(first["glb_sha256"],second["glb_sha256"])
            with self.assertRaises(FileExistsError):art.build_facades(source,p/"v4a")
    def test_projections_are_small_and_materials_have_no_external_urls(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/"fixture.json";self.fixture(source)
            report=art.build_facades(source,p/"out")
            self.assertLessEqual(report["max_outward_projection_m"],0.35)
            self.assertGreater(report["detail_triangles"],100)
            b=(p/"out/JED_AlBalad_ArchitecturalDetails_V4.glb").read_bytes()
            n=struct.unpack_from("<I",b,12)[0]
            document=json.loads(b[20:20+n])
            self.assertEqual(len(document["materials"]),3)
            self.assertFalse("images" in document)
            self.assertFalse("extensionsUsed" in document)
if __name__=="__main__":unittest.main(verbosity=2)
