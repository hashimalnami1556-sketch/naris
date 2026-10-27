"""Offline structural contracts only. This does not compile Unreal C++."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisStage32CombatComponent.h"
SOURCE = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisStage32CombatComponent.cpp"

class CombatContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = HEADER.read_text(encoding="utf-8")
        cls.s = SOURCE.read_text(encoding="utf-8")

    def test_atomic_stamina(self):
        self.assertLess(self.s.index("Montage_Play(Montage)"), self.s.index("Stamina-=Cost"))
        self.assertIn("if(Anim->Montage_Play(Montage)<=0.f)return false", self.s)

    def test_montage_end_is_bound(self):
        self.assertIn("Delegate.BindUObject(this,&UNarisStage32CombatComponent::OnMontageEnded)", self.s)
        self.assertIn("Montage_SetEndDelegate(Delegate,Montage)", self.s)

    def test_cleanup_on_endplay(self):
        self.assertIn("EndPlay(const EEndPlayReason::Type", self.h)
        self.assertIn("ClearActiveMontageBinding();Super::EndPlay(Reason)", self.s)

    def test_damage_windows_and_dedup(self):
        self.assertIn("BeginHitWindow()", self.s)
        self.assertIn("EndHitWindow()", self.s)
        self.assertIn("AlreadyHit.Contains(Other)", self.s)

    def test_team_filter(self):
        self.assertIn("TeamId==Target->TeamId", self.s)
        self.assertIn("bAllowFriendlyFire", self.h)

    def test_invulnerability(self):
        self.assertIn("StateAge<DodgeInvulnerabilitySeconds", self.s)

    def test_invalid_damage_rejected(self):
        self.assertIn("!FMath::IsFinite(Amount)", self.s)

    def test_telemetry_hook(self):
        self.assertIn("FNarisVitalsChanged", self.h)
        self.assertIn("OnVitalsChanged.Broadcast(Health,Stamina)", self.s)

    def test_recovery_and_regen(self):
        self.assertIn("StateAge>=RecoverySeconds", self.s)
        self.assertIn("StaminaRegenPerSecond", self.s)

    def test_no_unverified_engine_claim(self):
        self.assertNotIn("shipping_verified", self.s)

if __name__ == "__main__":
    unittest.main()
