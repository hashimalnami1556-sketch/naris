from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWorldStateSubsystem.h"
CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWorldStateSubsystem.cpp"
NPC = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisDailyNPC.cpp"
TYPES = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"

class WorldStateBridgeContract(unittest.TestCase):
    def test_saved_world_state_exists(self):
        text = TYPES.read_text(encoding="utf-8")
        for token in ("float WorldHour", "ENarisWeatherState WeatherState", "int32 WorldDay"):
            self.assertIn(token, text)

    def test_world_state_subsystem_advances_and_wraps_time(self):
        h = PUB.read_text(encoding="utf-8")
        cpp = CPP.read_text(encoding="utf-8")
        for token in ("UNarisWorldStateSubsystem", "SetWorldHour", "AdvanceGameHours", "SetWeatherState", "GetWorldHour"):
            self.assertIn(token, h)
        for token in ("FMath::Fmod", "WorldDay +=", "Runtime->SaveState"):
            self.assertIn(token, cpp)

    def test_world_state_broadcasts_to_npcs(self):
        cpp = CPP.read_text(encoding="utf-8")
        self.assertIn("TActorIterator<ANarisDailyNPC>", cpp)
        self.assertIn("NPC->SetWorldHour", cpp)
        self.assertIn("NPC->SetStormActive", cpp)

    def test_npc_prefers_authoritative_world_state(self):
        npc = NPC.read_text(encoding="utf-8")
        self.assertIn("GetSubsystem<UNarisWorldStateSubsystem>()", npc)
        self.assertIn("WorldState->GetWorldHour()", npc)

if __name__=="__main__":
    unittest.main()
