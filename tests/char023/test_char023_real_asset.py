"""Exact source/art integration tests. Skipped when user assets unavailable on CI."""
import hashlib, json, os, sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / 'tools' / 'assetforge'))
from char023_weapon_review import (read_glb,audit_source,audit_outputs,
    accessor_array,choose_grip,scan_image_digests,EXPECTED_SOURCE_SHA256)

class ActualArtContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get('NARIS_CHAR023_SOURCE')
        target=os.environ.get('NARIS_CHAR023_OUTPUT')
        if not source or not target:
            raise unittest.SkipTest('Source GLB is a user handoff and not checked into CI; offline real-art result recorded separately.')
        cls.source=Path(source);cls.out=Path(target);cls.original_bytes=cls.source.read_bytes()
        cls.doc,cls.blob=read_glb(cls.source)
        cls.pr,cls.tri,cls.lab,cls.masks=audit_source(cls.doc,cls.blob,hashlib.sha256(cls.original_bytes).hexdigest())
        cls.review=read_glb(cls.out/'NARIS_CHAR023_SectionReview.glb')
        cls.hero=read_glb(cls.out/'NARIS_CHAR023_HeroWithoutWeapon_REVIEW.glb')
        cls.weapon=read_glb(cls.out/'NARIS_CHAR023_RigidWeaponCandidate_REVIEW.glb')
    def test_source_hash_fixed(self):
        self.assertEqual(hashlib.sha256(self.original_bytes).hexdigest(),EXPECTED_SOURCE_SHA256)
    def test_exact_component_budget(self):
        self.assertEqual(len(np.unique(self.lab)),529)
        self.assertEqual([int(self.masks[x].sum()) for x in ('body','guard','blade')],[48052,592,1242])
    def test_original_payload_preserved_in_all_variants(self):
        for d,b in (self.review,self.hero,self.weapon):
            self.assertTrue(b.startswith(self.blob));self.assertGreaterEqual(len(b),len(self.blob))
    def test_extraction_preserves_all_original_faces_and_material(self):
        pos=accessor_array(self.doc,self.blob,0)
        grip=choose_grip(pos[np.unique(self.tri[self.masks['guard']])])
        self.assertTrue(audit_outputs(self.doc,self.blob,self.masks,grip,self.review,self.weapon,self.hero)['all_original_faces_accounted_for'])
    def test_rigid_weapon_has_no_skin_or_animation(self):
        d,b=self.weapon;self.assertNotIn('skins',d);self.assertNotIn('animations',d)
        self.assertEqual(len(d['meshes'][0]['primitives']),2)
        self.assertEqual(sum(d['accessors'][p['indices']]['count']//3 for p in d['meshes'][0]['primitives']),1834)
    def test_hero_keeps_original_animation(self):
        d,b=self.hero
        self.assertEqual(d['skins'],self.doc['skins']);self.assertEqual(d['animations'],self.doc['animations'])
        self.assertEqual(d['accessors'][d['meshes'][0]['primitives'][0]['indices']]['count']//3,48052)
    def test_original_jpeg_texture_data_same(self):
        imgs=scan_image_digests(self.doc,self.blob);self.assertEqual(len(imgs),3)
        for variant in (self.review,self.hero,self.weapon):
            self.assertEqual(imgs,scan_image_digests(*variant))
    def test_source_geometry_not_changed_by_tool(self):
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(),EXPECTED_SOURCE_SHA256)
    def test_grip_distance_production_gate_is_blocked(self):
        q=json.loads((self.out/'qa_report.json').read_text())
        self.assertEqual(q['status'],'REVIEW_READY_NOT_PRODUCTION')
        self.assertGreater(q['grip_to_hands_source_units']['hand_L'],.20)
        self.assertEqual(q['ue_socket_creation'],'NOT_RUN')

if __name__=='__main__':unittest.main()
