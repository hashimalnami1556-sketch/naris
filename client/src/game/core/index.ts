/**
 * Core Game Systems - تصدير جميع أنظمة اللعبة الأساسية
 */

// Event System
export { EventSystem, gameEvents } from './EventSystem';

// State Management
export { StateManager, gameState } from './StateManager';

// Configuration
export { ConfigManager, config } from './ConfigManager';

// Asset Loading
export { AssetLoader, assetLoader } from './AssetLoader';

// Character System
export { CharacterFactory, characterFactory } from './CharacterFactory';
export type { CharacterMesh } from './CharacterFactory';

// Game Renderer
export { GameRenderer, gameRenderer } from './GameRenderer';

// Camera Control
export { CameraController, cameraController } from './CameraController';
export type { CameraMode, CameraConfig } from './CameraController';

// Character Control
export { CharacterController, characterController } from './CharacterController';
export type { CharacterMovementConfig } from './CharacterController';

// Combat System
export { CombatSystem, combatSystem } from './CombatSystem';
export type { CombatAction, CombatLog } from './CombatSystem';

// Enemy AI
export { EnemyAI, enemyAI } from './EnemyAI';
export type { EnemyInstance, AIBehavior } from './EnemyAI';

// Weather System
export { WeatherSystem, weatherSystem } from './WeatherSystem';
export type { WeatherState, DayNightState } from './WeatherSystem';

// Quest System
export { QuestSystem, questSystem } from './QuestSystem';
export type { QuestTracker, QuestFilter } from './QuestSystem';

// Achievement System
export { AchievementSystem, achievementSystem } from './AchievementSystem';
export type { AchievementTracker, AchievementProgress } from './AchievementSystem';

// Input Manager
export { InputManager, inputManager } from './InputManager';
export type { InputAction, InputBinding, InputState } from './InputManager';

// Particle System
export { ParticleSystem, particleSystem } from './ParticleSystem';
export type { ParticleType, ParticleEmitterConfig } from './ParticleSystem';

// Animation System
export { AnimationSystem, animationSystem } from './AnimationSystem';
export type { AnimationState, AnimationConfig } from './AnimationSystem';

// Sound System
export { SoundSystem, soundSystem } from './SoundSystem';
export type { SoundType, SoundConfig } from './SoundSystem';

// VFX Manager
export { VFXManager, vfxManager } from './VFXManager';
export type { VFXType, VFXConfig } from './VFXManager';
