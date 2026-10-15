"""NARIS Fiery Demon native boss offline regression contract.
Not evidence of C++ compilation or actual Unreal PIE gameplay.
"""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
PUB=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Public/NarisFieryDemonBoss.h"
CPP=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisFieryDemonBoss.cpp"
BASE=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
IMPORTER=ROOT/"tools/unreal/import_fiery_demon_runtime.py"

class NativeBossContracts(unittest.TestCase):
    def test_native_boss_reuses_gameplay_state_machine(self):
        header=PUB.read_text(encoding="utf-8")
        self.assertIn("public ABoneBeastBoss",header)
        self.assertIn("NarisFieryDemonBoss.generated.h",header)

    def test_not_mark_full_demo_complete(self):
        code=CPP.read_text(encoding="utf-8")
        for token in ('BossProgressId = TEXT("FieryDemon")',
                      'FallbackMaxHealth = 6200.f;',
                      'bCompleteDemoOnDefeat = false;',
                      'RequiredCompanionId.Empty();'):
            self.assertIn(token,code)

    def test_two_boss_phases(self):
        code=CPP.read_text(encoding="utf-8")
        self.assertIn("FallbackPhase2HealthPercent = 0.55f;",code)
        self.assertIn("FallbackPhase3HealthPercent = 0.f;",code)

    def test_damage_follows_attack_animation(self):
        code=CPP.read_text(encoding="utf-8")
        for token in ("bImmediateSmokeAttackImpact = false;",
                      "GetPendingAttackId()", "SetTimer(",
                      "CommitAttackImpact(PlayerPawn)", "CancelAttack()"):
            self.assertIn(token,code)

    def test_other_boss_companion_gate_preserved(self):
        code=BASE.read_text(encoding="utf-8")
        self.assertIn("RequiredCompanionId.IsEmpty()",code)
        self.assertIn("IsCompanionUnlocked(RequiredCompanionId)",code)

    def test_unreal_editor_code_parses(self):
        code=IMPORTER.read_text(encoding="utf-8")
        ast.parse(code)
        self.assertIn("/Script/NARIS_W04.NarisFieryDemonBoss",code)

    def test_qa_only_by_default_and_real_player_start(self):
        code=IMPORTER.read_text(encoding="utf-8")
        for token in ("QA_MAP", "NARIS_ALLOW_MAP_EDIT", "PlayerStart",
                      "NARIS_QA_CollisionFloor", "NARIS_FieryDemon_EliteBoss",
                      "save_current_level()"):
            self.assertIn(token,code)

    def test_no_fabricated_pie_claims(self):
        code=IMPORTER.read_text(encoding="utf-8")
        self.assertIn('"pie_tested":False',code)
        self.assertIn('"shipping_approved":False',code)

if __name__=="__main__":
    unittest.main()
