from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class CombatDefenseEssencePauseContractTests(unittest.TestCase):
    def test_combat_result_records_evade(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("bool bEvaded = false", types)

    def test_incoming_hits_use_invulnerability_then_parry(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisCombatComponent.cpp"
        )
        self.assertIn("if (IsInvulnerable())", source)
        self.assertIn("Result.bEvaded = true", source)
        self.assertIn("const bool bParry = IsParryWindowActive()", source)
        self.assertIn("ParryWindowEndTime = -1.f", source)
        self.assertIn("ResolveHit(BaseDamage, PoiseDamage, bParry, bCritical)", source)

    def test_parry_reward_happens_on_resolved_parry_not_button_press(self) -> None:
        combat = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisCombatComponent.cpp"
        )
        hero = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn("if (bParried)", combat)
        self.assertIn("AddResonance(15.f)", combat)

        parry_body = re.search(
            r"void ANarisHeroCharacter::Parry\(\)\s*\{(.*?)\n\}",
            hero,
            re.S,
        )
        self.assertIsNotNone(parry_body)
        self.assertIn("OpenParryWindow(ParryWindowSeconds)", parry_body.group(1))
        self.assertNotIn("AddResonance", parry_body.group(1))

    def test_dodge_spends_energy_and_opens_iframes(self) -> None:
        hero = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn("Energy->Spend(DodgeEnergyCost)", hero)
        self.assertIn(
            "Combat->OpenInvulnerabilityWindow(DodgeInvulnerabilitySeconds)",
            hero,
        )

    def test_unreal_damage_routes_through_defense_resolution(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn("virtual float TakeDamage(", header)
        self.assertIn("Combat->ResolveIncomingHit", source)

    def test_essence_cycle_wraps_all_five_essences(self) -> None:
        energy = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisEnergyComponent.cpp"
        )
        self.assertIn("constexpr int32 EssenceCount = 5", energy)
        self.assertIn("CycleEssence(int32 Direction)", energy)
        for key in (
            "EssenceNarisFlame",
            "EssenceAsh",
            "EssenceAether",
            "EssenceVoid",
            "EssenceRadiant",
        ):
            self.assertIn(key, energy)

    def test_keyboard_and_gamepad_bind_essence_and_pause(self) -> None:
        ini = read("unreal/NARIS_W04/Config/DefaultInput.ini")
        for token in (
            'ActionName="EssenceNext",Key=(KeyName="X")',
            'ActionName="EssenceNext",Key=(KeyName="Gamepad_DPad_Right")',
            'ActionName="EssencePrevious",Key=(KeyName="Z")',
            'ActionName="EssencePrevious",Key=(KeyName="Gamepad_DPad_Left")',
            'ActionName="Pause",Key=(KeyName="Escape")',
            'ActionName="Pause",Key=(KeyName="Gamepad_Special_Right")',
        ):
            self.assertIn(token, ini)

    def test_pause_binding_executes_while_paused(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn('BindAction(TEXT("Pause")', source)
        self.assertIn("PauseBinding.bExecuteWhenPaused = true", source)
        self.assertIn("UGameplayStatics::IsGamePaused(this)", source)
        self.assertIn("UGameplayStatics::SetGamePaused(this, !bPaused)", source)

    def test_hud_exposes_active_essence(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("GetActiveEssenceDisplayName()", source)
        self.assertIn('"HUDEssence"', source)


if __name__ == "__main__":
    unittest.main()
