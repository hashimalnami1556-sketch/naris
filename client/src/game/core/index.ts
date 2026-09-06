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
