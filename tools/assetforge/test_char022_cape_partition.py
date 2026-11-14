"""Run with NARIS_CHAR022_SOURCE pointing to the original SkinFixed GLB."""
import os, unittest, hashlib, copy
from pathlib import Path
import numpy as np
from char022_repair_skin import read_glb,array
from char022_cape_partition import partition,SOURCE_SHA

class CapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=os.environ.get("NARIS_CHAR022_SOURCE")
        if not src:
            raise RuntimeError("NARIS_CHAR022_SOURCE must point to verified SkinFixed GLB")
        cls.src=Path(src)
        cls.doc,cls.bin=read_glb(cls.src)
        cls.new,cls.data,cls.ids,cls.report=partition(cls.doc,cls.bin)
        cls.prims=cls.new["meshes"][0]["primitives"]
        cls.orig=array(cls.doc,cls.bin,3).reshape(-1,3)
    def test_source_digest(self):
        self.assertEqual(hashlib.sha256(self.src.read_bytes()).hexdigest(),SOURCE_SHA)
    def test_partition_exact_and_ordered(self):
        ids=self.ids
        self.assertEqual(len(ids),19731)
        self.assertEqual(len(np.unique(ids)),len(ids))
        keep=np.ones(len(self.orig),dtype=bool);keep[ids]=False
        np.testing.assert_array_equal(array(self.new,self.data,self.prims[0]["indices"]).reshape(-1,3),self.orig[keep])
        np.testing.assert_array_equal(array(self.new,self.data,self.prims[1]["indices"]).reshape(-1,3),self.orig[ids])
    def test_original_payload_unchanged(self):
        self.assertEqual(self.data[:len(self.bin)],self.bin)
    def test_art_skin_and_animation_unchanged(self):
        for key in ("nodes","skins","animations","images","materials","textures","samplers"):
            self.assertEqual(self.doc[key],self.new[key],key)
        for primitive in self.prims:
            self.assertEqual(primitive["attributes"],self.doc["meshes"][0]["primitives"][0]["attributes"])
            self.assertEqual(primitive["material"],0)
    def test_mask_stays_behind_body(self):
        verts=array(self.doc,self.bin,0)[self.orig[self.ids]]
        self.assertTrue((verts[:,:,2]<-.065).all())
        self.assertTrue((verts[:,:,1]>.14).all())
        self.assertTrue((verts[:,:,1]<.82).all())
    def test_no_claim_of_cloth(self):
        self.assertEqual(self.report["cloth_simulation"],"NOT_RUN")
        self.assertEqual(self.report["selection_status"],"REVIEW_REQUIRED")
        self.assertGreater(self.report["shared_boundary_vertices"],0)
    def test_reject_altered_layout(self):
        changed=copy.deepcopy(self.doc);changed["nodes"][18].pop("skin")
        with self.assertRaises(ValueError):partition(changed,self.bin)
    def test_accessor_integrity(self):
        for p in self.prims:
            a=self.new["accessors"][p["indices"]];v=self.new["bufferViews"][a["bufferView"]]
            self.assertEqual(v["byteOffset"]%4,0)
            self.assertEqual(a["count"]%3,0)
            self.assertEqual(v["byteLength"],a["count"]*2)
        self.assertEqual(self.new["buffers"][0]["byteLength"],len(self.data))
if __name__=="__main__":unittest.main()
