from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
ENV_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWeatherEnvironmentSubsystem.h"
ENV_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWeatherEnvironmentSubsystem.cpp"
GAME_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWeatherGameplayComponent.h"
GAME_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWeatherGameplayComponent.cpp"
HERO_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
HERO_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"

class WeatherEnvironmentGameplayContract(unittest.TestCase):
    def test_environment_subsystem_exposes_surface_state(self):
        h=ENV_H.read_text(encoding="utf-8")
        for token in ("UNarisWeatherEnvironmentSubsystem","GetSnowLevel","GetWetness","GetMud","GetWindStrength","UpdateEnvironmentState"):
            self.assertIn(token,h)

    def test_environment_derives_state_from_authoritative_weather(self):
        cpp=ENV_CPP.read_text(encoding="utf-8")
        for token in ("UNarisWorldStateSubsystem","GetWeatherState()","ENarisWeatherState::Snow","ENarisWeatherState::HeavyRain","ENarisWeatherState::Sandstorm","FMath::FInterpTo"):
            self.assertIn(token,cpp)

    def test_gameplay_component_exposes_multipliers_and_damage(self):
        h=GAME_H.read_text(encoding="utf-8")
        cpp=GAME_CPP.read_text(encoding="utf-8")
        for token in ("UNarisWeatherGameplayComponent","GetMoveSpeedMultiplier","GetVisibilityMultiplier","RefreshWeatherProfile"):
            self.assertIn(token,h)
        for token in ("HealthDrainPerSecond","CombatComponent->Health","Hero->RefreshMovementSpeed","Thunderstorm","Blizzard","Sandstorm"):
            self.assertIn(token,cpp)

    def test_hero_routes_speed_through_weather_component(self):
        h=HERO_H.read_text(encoding="utf-8")
        cpp=HERO_CPP.read_text(encoding="utf-8")
        for token in ("UNarisWeatherGameplayComponent","WeatherGameplay","RefreshMovementSpeed","IsSprinting"):
            self.assertIn(token,h)
        self.assertIn("WeatherGameplay->GetMoveSpeedMultiplier()",cpp)

if __name__=="__main__":
    unittest.main()
