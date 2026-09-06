/**
 * Naris Realms - Game Types Definition
 * تعريف جميع الأنواع والواجهات لمحرك اللعبة
 * Version: 1.0.0
 */

// ─────────────────────────────────────────────────────────────
// 🎮 أنواع الشخصيات (Character Types)
// ─────────────────────────────────────────────────────────────

export type CharacterId = 'ash' | 'rune' | 'kor';
export type CharacterRole = 'warrior' | 'mage' | 'tank';

export interface CharacterStats {
  health: number;
  maxHealth: number;
  energy: number;
  maxEnergy: number;
  speed: number;
  baseDamage: number;
  defense: number;
  weaponTier: number;
}

export interface CharacterProfile {
  id: CharacterId;
  name: string;
  role: CharacterRole;
  description: string;
  stats: CharacterStats;
  abilities: Ability[];
  weaponData: WeaponData;
  colorScheme: {
    primary: string;
    secondary: string;
    accent: string;
    energy: string;
  };
  scale: number;
  speed: number;
  baseHealth: number;
  baseDamage: number;
}

// ─────────────────────────────────────────────────────────────
// ⚔️ أنواع القتال والقدرات (Combat Types)
// ─────────────────────────────────────────────────────────────

export interface Ability {
  id: string;
  name: string;
  key: string;
  description: string;
  cooldown: number;
  currentCooldown: number;
  damage: number;
  range: number;
  effect: string;
  animationDuration: number;
  energyCost: number;
}

export interface WeaponData {
  id: string;
  name: string;
  type: string;
  baseDamage: number;
  damageType: 'physical' | 'fire' | 'arcane' | 'void';
  secondaryDamage?: number;
  secondaryType?: string;
  range: number;
  attackSpeed: number;
  tier: number;
  upgrades: WeaponUpgrade[];
}

export interface WeaponUpgrade {
  tier: number;
  description: string;
  damageBonus: number;
  speedBonus: number;
  effect: string;
}

export interface Enemy {
  id: string;
  type: string;
  health: number;
  maxHealth: number;
  damage: number;
  speed: number;
  position: Vector3;
  weaknesses: DamageType[];
  resistances: DamageType[];
  abilities: EnemyAbility[];
  ai: EnemyAI;
  lootTable: LootDrop[];
}

export interface EnemyAbility {
  name: string;
  damage: number;
  range: number;
  cooldown: number;
  currentCooldown: number;
  effect: string;
}

export interface EnemyAI {
  type: 'idle' | 'patrol' | 'aggressive' | 'boss';
  speed: number;
  attackRange: number;
  detectionRange: number;
  behaviour: string;
}

export type DamageType = 'physical' | 'fire' | 'arcane' | 'void' | 'light' | 'water';

export interface DamageCalculation {
  baseDamage: number;
  weaponDamage: number;
  multiplier: number;
  weakness: number;
  resistance: number;
  finalDamage: number;
}

export interface LootDrop {
  itemId: string;
  quantity: number;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  dropRate: number;
}

// ─────────────────────────────────────────────────────────────
// 🌍 أنواع البيئات والعالم (Environment Types)
// ─────────────────────────────────────────────────────────────

export type RealmId = 'ash_gate' | 'bell_marsh' | 'twilight_castle';

export interface RealmData {
  id: RealmId;
  name: string;
  description: string;
  size: Vector2;
  terrainHeightMap: number[][];
  environmentType: EnvironmentType;
  weatherSystem: WeatherSystem;
  dayNightCycle: DayNightCycle;
  spawningZones: SpawningZone[];
  waystones: Waystone[];
  landmarks: Landmark[];
  hazards: Hazard[];
}

export type EnvironmentType = 'ruins' | 'swamp' | 'castle';

export interface WeatherSystem {
  currentWeather: WeatherState;
  rainIntensity: number;
  windStrength: number;
  temperature: number;
  visibility: number;
  weatherCycle: WeatherTransition[];
}

export interface WeatherState {
  type: 'clear' | 'rain' | 'storm' | 'sand_storm' | 'snow' | 'fog';
  intensity: number;
  duration: number;
}

export interface WeatherTransition {
  from: string;
  to: string;
  duration: number;
  probability: number;
}

export interface DayNightCycle {
  timeOfDay: number; // 0-1440 (minutes)
  dayLength: number;
  currentPhase: 'dawn' | 'day' | 'dusk' | 'night';
  lightIntensity: number;
  ambientColor: string;
}

export interface SpawningZone {
  id: string;
  position: Vector3;
  radius: number;
  enemyTypes: string[];
  spawnRate: number;
  maxEnemies: number;
}

export interface Waystone {
  id: string;
  name: string;
  position: Vector3;
  discovered: boolean;
  unlocked: boolean;
  questsAvailable: string[];
}

export interface Landmark {
  id: string;
  name: string;
  position: Vector3;
  type: string;
  discovered: boolean;
  description: string;
  rewards: Reward[];
}

export interface Hazard {
  id: string;
  type: string;
  position: Vector3;
  radius: number;
  damage: number;
  damageType: DamageType;
}

// ─────────────────────────────────────────────────────────────
// 📦 أنواع الجرد والعناصر (Inventory Types)
// ─────────────────────────────────────────────────────────────

export interface InventoryItem {
  itemId: string;
  quantity: number;
  slot?: number;
  equipped?: boolean;
}

export interface ItemData {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'consumable' | 'material' | 'quest';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  description: string;
  value: number;
  weight: number;
  effects?: string[];
  stackable: boolean;
  maxStack: number;
}

export interface Crafting {
  recipeId: string;
  ingredients: InventoryItem[];
  result: ItemData;
  craftingTime: number;
  level: number;
  category: string;
}

// ─────────────────────────────────────────────────────────────
// 📋 أنواع المهام والإنجازات (Quest & Achievement Types)
// ─────────────────────────────────────────────────────────────

export interface Quest {
  id: string;
  title: string;
  description: string;
  objectives: QuestObjective[];
  rewards: Reward[];
  status: 'available' | 'active' | 'completed' | 'failed';
  type: 'main' | 'side' | 'daily';
  giver: string;
  giverLocation: string;
}

export interface QuestObjective {
  id: string;
  description: string;
  type: 'kill' | 'collect' | 'reach' | 'interact' | 'discover';
  target: string;
  current: number;
  required: number;
  completed: boolean;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  condition: AchievementCondition;
  unlocked: boolean;
  unlockedAt?: number;
  reward: Reward;
}

export interface AchievementCondition {
  type: string;
  value: number;
}

export interface Reward {
  type: 'shards' | 'item' | 'experience' | 'ability';
  value: number;
  itemId?: string;
}

// ─────────────────────────────────────────────────────────────
// 💾 أنواع الحفظ والإعدادات (Save & Settings Types)
// ─────────────────────────────────────────────────────────────

export interface GameSaveData {
  version: string;
  timestamp: number;
  playTime: number;
  currentCharacter: CharacterId;
  position: Vector3;
  realm: RealmId;
  player: PlayerGameState;
  inventory: InventoryItem[];
  quests: Quest[];
  achievements: Achievement[];
  landmarks: string[];
  waystones: string[];
  settings: GameSettings;
}

export interface PlayerGameState {
  health: number;
  energy: number;
  shards: number;
  experience: number;
  level: number;
  weaponTier: number;
  unlockedAbilities: string[];
  currentQuests: string[];
  completedQuests: string[];
  allies: string[];
}

export interface GameSettings {
  difficulty: 'story' | 'normal' | 'hard' | 'extreme';
  language: 'ar' | 'en';
  masterVolume: number;
  musicVolume: number;
  sfxVolume: number;
  ambientVolume: number;
  graphicsQuality: 'low' | 'medium' | 'high' | 'ultra';
  resolution: string;
  fpsTarget: number;
  vSync: boolean;
  reducedMotion: boolean;
  subtitles: boolean;
  hudScale: number;
  showMinimap: boolean;
  showQuestMarkers: boolean;
}

// ─────────────────────────────────────────────────────────────
// 🎯 أنواع الحالة والأحداث (State & Event Types)
// ─────────────────────────────────────────────────────────────

export interface GameState {
  isRunning: boolean;
  isPaused: boolean;
  currentRealm: RealmId;
  currentCharacter: CharacterId;
  playerState: PlayerGameState;
  inventory: InventoryItem[];
  quests: Quest[];
  achievements: Achievement[];
  settings: GameSettings;
  weather: WeatherState;
  timeOfDay: number;
  fps: number;
}

export interface GameEvent {
  type: string;
  data: any;
  timestamp: number;
}

export type GameEventType =
  | 'character_switched'
  | 'ability_used'
  | 'enemy_defeated'
  | 'item_collected'
  | 'quest_completed'
  | 'achievement_unlocked'
  | 'damage_taken'
  | 'heal_applied'
  | 'level_up'
  | 'game_paused'
  | 'game_resumed'
  | 'realm_changed'
  | 'weather_changed'
  | 'landmark_discovered'
  | 'waystone_activated';

// ─────────────────────────────────────────────────────────────
// 🔢 أنواع الرياضيات (Math Types)
// ─────────────────────────────────────────────────────────────

export interface Vector2 {
  x: number;
  y: number;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Vector4 {
  x: number;
  y: number;
  z: number;
  w: number;
}

export interface Quaternion {
  x: number;
  y: number;
  z: number;
  w: number;
}

export interface Matrix4x4 {
  data: number[];
}

// ─────────────────────────────────────────────────────────────
// 🎬 أنواع الكاميرا والعرض (Camera & Rendering)
// ─────────────────────────────────────────────────────────────

export interface CameraConfig {
  mode: 'third_person' | 'cinematic';
  distance: number;
  height: number;
  angle: number;
  fov: number;
  nearClip: number;
  farClip: number;
  smoothing: number;
}

export interface RenderSettings {
  resolution: Vector2;
  dpi: number;
  targetFPS: number;
  vSync: boolean;
  shadowQuality: 'low' | 'medium' | 'high';
  particleQuality: 'low' | 'medium' | 'high';
  textureQuality: 'low' | 'medium' | 'high';
}

// ─────────────────────────────────────────────────────────────
// 🎵 أنواع الصوت (Audio Types)
// ─────────────────────────────────────────────────────────────

export interface AudioClip {
  id: string;
  name: string;
  path: string;
  duration: number;
  volume: number;
  loop: boolean;
}

export interface MusicTrack {
  id: string;
  name: string;
  realm: RealmId;
  phase: 'dawn' | 'day' | 'dusk' | 'night' | 'boss';
  bpm: number;
  duration: number;
}

// ─────────────────────────────────────────────────────────────
// 🤝 أنواع الحلفاء والتفاعل (Allies & Interaction)
// ─────────────────────────────────────────────────────────────

export interface Ally {
  id: string;
  name: string;
  type: 'wolf' | 'spirit' | 'raven' | 'knight';
  health: number;
  maxHealth: number;
  damage: number;
  abilities: Ability[];
  ai: EnemyAI;
  status: 'active' | 'resting' | 'dead';
}

export interface DialogueLine {
  id: string;
  speaker: string;
  text: string;
  choices?: DialogueChoice[];
}

export interface DialogueChoice {
  id: string;
  text: string;
  nextDialogueId: string;
  consequences?: string[];
}

export interface NPC {
  id: string;
  name: string;
  position: Vector3;
  dialogueTree: DialogueLine[];
  quests: string[];
  inventory: InventoryItem[];
  faction: string;
  reputation: number;
}

// ─────────────────────────────────────────────────────────────
// 🚀 أنواع النظام والأداء (System & Performance)
// ─────────────────────────────────────────────────────────────

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  drawCalls: number;
  triangles: number;
  particles: number;
  memoryUsage: number;
  gpuMemory: number;
}

export interface DebugSettings {
  showBounds: boolean;
  showColliders: boolean;
  showPerformance: boolean;
  showLights: boolean;
  showCamera: boolean;
  pauseAI: boolean;
  infiniteEnergy: boolean;
  instantAbilities: boolean;
}

export interface AppConfig {
  version: string;
  buildDate: string;
  environment: 'development' | 'staging' | 'production';
  debug: boolean;
  debugSettings: DebugSettings;
  renderSettings: RenderSettings;
  audioEnabled: boolean;
  maxFrameRate: number;
  targetFrameRate: number;
  useWorkers: boolean;
}

// ─────────────────────────────────────────────────────────────
// 🛠️ أنواع المساعدين والأدوات (Helper & Utility Types)
// ─────────────────────────────────────────────────────────────

export interface ColorRGB {
  r: number;
  g: number;
  b: number;
}

export interface ColorRGBA {
  r: number;
  g: number;
  b: number;
  a: number;
}

export interface Range {
  min: number;
  max: number;
}

export interface Bounds2D {
  x: Range;
  y: Range;
}

export interface Bounds3D {
  x: Range;
  y: Range;
  z: Range;
}

// ─────────────────────────────────────────────────────────────
// 📊 نوع رد الاتصال (Callback Types)
// ─────────────────────────────────────────────────────────────

export type EventCallback = (event: GameEvent) => void;
export type UpdateCallback = (deltaTime: number) => void;
export type RenderCallback = (deltaTime: number) => void;
export type LoadCallback = (progress: number) => void;

// ─────────────────────────────────────────────────────────────
// ✅ تصدير جميع الأنواع
// ─────────────────────────────────────────────────────────────

export default {
  CharacterId,
  CharacterRole,
  CharacterStats,
  CharacterProfile,
  Ability,
  WeaponData,
  WeaponUpgrade,
  Enemy,
  EnemyAbility,
  EnemyAI,
  DamageType,
  DamageCalculation,
  LootDrop,
  RealmId,
  RealmData,
  EnvironmentType,
  WeatherSystem,
  WeatherState,
  WeatherTransition,
  DayNightCycle,
  SpawningZone,
  Waystone,
  Landmark,
  Hazard,
  InventoryItem,
  ItemData,
  Crafting,
  Quest,
  QuestObjective,
  Achievement,
  AchievementCondition,
  Reward,
  GameSaveData,
  PlayerGameState,
  GameSettings,
  GameState,
  GameEvent,
  GameEventType,
  Vector2,
  Vector3,
  Vector4,
  Quaternion,
  Matrix4x4,
  CameraConfig,
  RenderSettings,
  AudioClip,
  MusicTrack,
  Ally,
  DialogueLine,
  DialogueChoice,
  NPC,
  PerformanceMetrics,
  DebugSettings,
  AppConfig,
  ColorRGB,
  ColorRGBA,
  Range,
  Bounds2D,
  Bounds3D,
};
