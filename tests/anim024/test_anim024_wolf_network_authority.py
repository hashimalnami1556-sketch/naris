"""Source security regressions for multiplayer Celestial Wolf, ANIM-024.

These checks are deliberately NOT substitutes for a real Unreal server/client
replication test: they prevent regression in critical authority/ownership paths.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2] / "unreal/NARIS_W04/Source/NARIS_W04"
WOLF_H = (ROOT / "Public/CelestialWolf.h").read_text(encoding="utf-8")
WOLF_CPP = (ROOT / "Private/CelestialWolf.cpp").read_text(encoding="utf-8")
HERO_H = (ROOT / "Public/NarisHeroCharacter.h").read_text(encoding="utf-8")
HERO_CPP = (ROOT / "Private/NarisHeroCharacter.cpp").read_text(encoding="utf-8")


def body(code: str, class_name: str, method: str) -> str:
    match = re.search(r"\b" + re.escape(class_name) + r"::" + re.escape(method) + r"\s*\(", code)
    if not match:
        raise AssertionError(f"{class_name}::{method} missing")
    start = code.find("{", match.end())
    if start == -1:
        raise AssertionError(f"{class_name}::{method} body missing")
    depth = 0
    for pos in range(start, len(code)):
        if code[pos] == "{":
            depth += 1
        elif code[pos] == "}":
            depth -= 1
            if depth == 0:
                return code[start:pos + 1]
    raise AssertionError(f"{class_name}::{method} unclosed")


class WolfServerAuthorityContract(unittest.TestCase):
    def test_replicates_bond_and_mode_as_state(self):
        self.assertRegex(WOLF_H, r"UPROPERTY\(ReplicatedUsing=OnRep_Mode[^)]*\)\s*ENarisWolfMode\s+Mode")
        self.assertRegex(WOLF_H, r"UPROPERTY\(ReplicatedUsing=OnRep_Bonded[^)]*\)\s*bool\s+bBonded")
        self.assertIn("GetLifetimeReplicatedProps", WOLF_H)
        self.assertIn("DOREPLIFETIME(ACelestialWolf, Mode);", WOLF_CPP)
        self.assertIn("DOREPLIFETIME(ACelestialWolf, bBonded);", WOLF_CPP)

    def test_clients_receive_repnotify_ui_events(self):
        self.assertIn("void ACelestialWolf::OnRep_Mode()", WOLF_CPP)
        self.assertIn("OnModeChanged.Broadcast(Mode);", body(WOLF_CPP, "ACelestialWolf", "OnRep_Mode"))
        self.assertIn("void ACelestialWolf::OnRep_Bonded()", WOLF_CPP)
        self.assertIn("OnBonded.Broadcast();", body(WOLF_CPP, "ACelestialWolf", "OnRep_Bonded"))

    def test_server_is_only_authority_for_wolf_movement_and_hits(self):
        for method in ("Tick", "RequestAttack", "CommitAttackImpact", "BondWithPlayer",
                       "SetMode", "CycleMode", "SetTrackTarget"):
            with self.subTest(method=method):
                self.assertIn("HasAuthority()", body(WOLF_CPP, "ACelestialWolf", method))

    def test_client_beginplay_does_not_initialize_bond_from_local_save(self):
        source = body(WOLF_CPP, "ACelestialWolf", "BeginPlay")
        self.assertIn("if (!HasAuthority())", source)
        self.assertLess(source.index("if (!HasAuthority())"), source.index("IsCompanionUnlocked("))

    def test_no_direct_client_boss_damage(self):
        source = body(WOLF_CPP, "ACelestialWolf", "CommitAttackImpact")
        self.assertLess(source.index("if (!HasAuthority())"), source.index("ApplyDamageToEncounter("))

    def test_player_owned_rpc_used_to_route_client_interaction(self):
        self.assertIn("UFUNCTION(Server, Reliable)", HERO_H)
        self.assertIn("ServerInteractWithWolf(", HERO_H)
        self.assertIn("ServerInteractWithWolf_Implementation", HERO_CPP)
        src = body(HERO_CPP, "ANarisHeroCharacter", "Interact")
        self.assertIn("ServerInteractWithWolf(Wolf);", src)
        self.assertIn("HasAuthority()", src)
        server = body(HERO_CPP, "ANarisHeroCharacter", "ServerInteractWithWolf_Implementation")
        self.assertIn("Interaction->FindNearestInteractable() != Wolf", server)
        self.assertIn("Interaction->Interact();", server)

    def test_companion_mode_button_routes_to_server_rpc(self):
        self.assertIn("ServerCycleCompanionMode();", body(HERO_CPP, "ANarisHeroCharacter", "CycleCompanionMode"))
        self.assertIn("ServerCycleCompanionMode_Implementation", HERO_CPP)

    def test_unpaused_network_movement_probe_uses_character_movement_only_in_non_shipping(self):
        # A deterministic opt-in moving destination lets us verify *ongoing*
        # server->client movement after players joined, rather than only the
        # initially replicated world position at join time.
        follow = body(WOLF_CPP, "ACelestialWolf", "TickFollow")
        self.assertIn("#if !UE_BUILD_SHIPPING", follow)
        self.assertIn("NarisWolfNetProbeMarch", follow)
        self.assertIn("MoveTowards(ProbeDestination", follow)
        self.assertIn("#endif", follow)

    def test_debug_netprobe_emits_actual_authority_state_only_when_opted_in(self):
        self.assertIn("NarisWolfNetProbe", WOLF_CPP)
        self.assertIn("NARIS_WOLF_NET_PROBE", WOLF_CPP)


if __name__ == "__main__":
    unittest.main()
