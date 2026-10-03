# NARIS W04 — Weather Environment + Gameplay Runtime

## Implemented
- `UNarisWeatherEnvironmentSubsystem`
  - derives normalized SnowLevel, Wetness and Mud from authoritative `UNarisWorldStateSubsystem`;
  - derives WindStrength by weather severity;
  - timer-driven updates instead of per-frame work.
- `UNarisWeatherGameplayComponent`
  - reads authoritative weather;
  - exposes movement and visibility multipliers;
  - applies periodic health drain for hazardous weather profiles;
  - asks the hero to refresh walking/sprinting speed when the profile changes.
- `ANarisHeroCharacter`
  - owns WeatherGameplay;
  - routes WalkSpeed/SprintSpeed through the weather movement multiplier.

## Current tuning
- HeavyRain: move 0.92, visibility 0.82
- Thunderstorm: move 0.88, visibility 0.68
- Snow: move 0.90, visibility 0.88
- Blizzard: move 0.76, visibility 0.38, health -1.5/s
- Sandstorm: move 0.82, visibility 0.32, health -0.75/s
- AshStorm: move 0.85, visibility 0.42, health -0.5/s
- VoidStorm: move 0.80, visibility 0.28, health -2.0/s

These values are production tuning defaults, not final balance.

## Visual integration contract
The environment subsystem exposes runtime values but does not fabricate final binary assets. The Unreal material/FX pass should bind:
- SnowLevel → terrain/rock material snow blend and decals;
- Wetness → roughness/darkening/water droplets;
- Mud → landscape material blend, footprints and movement feedback;
- WindStrength → foliage wind, Niagara rain/snow/ash, cloth and ambient audio;
- VisibilityMultiplier → exponential-height-fog / local fog tuning through an authored presentation bridge.

Prefer a Material Parameter Collection and Niagara user parameters instead of scanning materials every update.

## Performance rules
- do not update every material instance each frame;
- one global environment state → MPC/FX broadcast;
- distant precipitation systems use Niagara scalability;
- storms must have quality tiers;
- gameplay modifier timer is 1 second, not Tick.

## Next production pass
- create the authored MPC and presentation actor;
- particle systems for rain/snow/ash/sand;
- thunder light/audio events;
- ground footprint/decal response;
- weather transition curves;
- indoor shelter volumes to suppress precipitation and harmful exposure.
