"""Static guard for NARIS W04 villain gameplay source and encounter data.

Does not compile Unreal or prove animation/AI pathfinding. Run from repo root:
    python -m unittest tools/ci/test_villain_encounter_contract.py -v
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "unreal" / "NARIS_W04" / "Source" / "NARIS_W04"
W04 = ROOT / "unreal" / "NARIS_W04" / "Content" / "NARIS" / "W04"
DATA = W04 / "Data" / "W04_VillainEncounterRoster.json"
MAP_SCRIPT = ROOT / "unreal/NARIS_W04/Content/Python/naris_author_w04_villains.py"
KNOWN = {
    "AshWretch", "BronzeSentinel", "BellWraith", "DrownedKnight",
    "ChainedGiant", "AshGatekeeper", "EclipseReaver",
}


class VillainRuntimeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = json.loads(DATA.read_text(encoding="utf-8"))
        cls.cpp = (CODE / "Private" / "NarisVillainCharacter.cpp").read_text(encoding="utf-8")
        cls.header = (CODE / "Public" / "NarisVillainCharacter.h").read_text(encoding="utf-8")
        cls.author = MAP_SCRIPT.read_text(encoding="utf-8")
        cls.layout = json.loads(
            (ROOT / "NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json")
            .read_text(encoding="utf-8")
        )

    def test_map_is_only_development_blockout(self):
        self.assertTrue(self.roster["developmentMap"].endswith("_Blockout"))
        self.assertNotEqual(self.roster["developmentMap"], self.roster["productionMap"])
        self.assertIn("production_ready", self.author)
        self.assertIn('False', self.author)

    def test_all_spawn_entries_well_formed(self):
        rows = self.roster["encounters"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(len({row["label"] for row in rows}), len(rows))
        zones = {zone["id"] for zone in self.layout["zones"]}
        for row in rows:
            self.assertIn(row["villain_id"], KNOWN)
            self.assertIn(row["zone"], zones)
            self.assertEqual(len(row["offset_m"]), 3)
            self.assertGreaterEqual(row["offset_m"][2], 0.5)
            self.assertLessEqual(row["offset_m"][2], 2.5)
            self.assertIn(row["villain_id"], self.cpp)

    def test_gameplay_and_animation_hooks_exist(self):
        for snippet in (
            "AutoPossessAI", "MoveToActor(", "MoveToLocation(",
            "LineOfSightTo(", "ApplyDamage(", "OnVillainDefeated.Broadcast",
            "ChangeState(ENarisVillainState::Dead)", "GetSkeletalMeshAsset()",
        ):
            self.assertIn(snippet, self.cpp)
        for snippet in ("CommitAttackImpact", "OnVillainAttackRequested",
                        "OnVillainPhaseTwo", "OnVillainDeath"):
            self.assertIn(snippet, self.header)

    def test_existing_lock_on_and_bonebeast_are_preserved(self):
        lockon = (CODE / "Private" / "NarisLockOnComponent.cpp").read_text(encoding="utf-8")
        hero = (CODE / "Private" / "NarisHeroCharacter.cpp").read_text(encoding="utf-8")
        self.assertIn("FindComponentByClass<UNarisCombatComponent>()", lockon)
        self.assertIn("TargetCombat->ResolveHit", hero)
        self.assertTrue((CODE / "Private" / "BoneBeastBoss.cpp").exists())

    def test_editor_placement_is_idempotent(self):
        self.assertIn("find_actor(actors, entry[\"label\"])", self.author)
        self.assertIn("set_editor_property(\"villain_id\"", self.author)
        self.assertIn("NavMeshBoundsVolume", self.author)


if __name__ == "__main__":
    unittest.main()
