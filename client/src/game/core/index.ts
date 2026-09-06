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

// Save System
export { SaveSystem, saveSystem } from './SaveSystem';
export type { SaveData } from './SaveSystem';

// Inventory System
export { InventorySystem, inventorySystem } from './InventorySystem';
export type { InventoryItem, Shard } from './InventorySystem';

// Crafting System
export { CraftingSystem, craftingSystem } from './CraftingSystem';
export type { CraftingRecipe } from './CraftingSystem';

// Dialogue System
export { DialogueSystem, dialogueSystem } from './DialogueSystem';
export type { DialogueLine, DialogueChoice, DialogueNode } from './DialogueSystem';

// Checkpoint System
export { CheckpointSystem, checkpointSystem } from './CheckpointSystem';
export type { Checkpoint } from './CheckpointSystem';

// World Manager
export { WorldManager, worldManager } from './WorldManager';
export type { World } from './WorldManager';

// Environment Director
export { EnvironmentDirector, environmentDirector } from './EnvironmentDirector';
export type { EnvironmentPreset } from './EnvironmentDirector';

// Day/Night System
export { DayNightSystem, dayNightSystem } from './DayNightSystem';
export type { TimeOfDay, TimeConfig } from './DayNightSystem';

// Lighting System
export { LightingSystem, lightingSystem } from './LightingSystem';
export type { Light } from './LightingSystem';

// Tutorial System
export { TutorialSystem, tutorialSystem } from './TutorialSystem';
export type { Hint, TutorialStep } from './TutorialSystem';

// Performance Monitor
export { PerformanceMonitor, performanceMonitor } from './PerformanceMonitor';
export type { PerformanceMetrics } from './PerformanceMonitor';

// Debug Overlay
export { DebugOverlay, debugOverlay } from './DebugOverlay';
export type { DebugInfo } from './DebugOverlay';

// Ally System
export { AllySystem, allySystem } from './AllySystem';
export type { Ally } from './AllySystem';

// Spirit System
export { SpiritSystem, spiritSystem } from './SpiritSystem';
export type { Spirit, SpiritType } from './SpiritSystem';
