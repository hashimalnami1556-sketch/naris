/**
 * HUD Component - واجهة المستخدم أثناء اللعب
 * يعرض جميع المعلومات الحية والعناصر التفاعلية
 */

import React, { useEffect, useState } from 'react';
import { gameEvents } from '../../game/core/EventSystem';
import { gameState } from '../../game/core/StateManager';
import { characterController } from '../../game/core/CharacterController';
import { CharacterInfoPanel } from './CharacterInfoPanel';
import { AbilityBar } from './AbilityBar';
import { Minimap } from './Minimap';
import { QuestTracker } from './QuestTracker';
import { EnemyHealthBar } from './EnemyHealthBar';

export interface HUDProps {
  onPauseGame: () => void;
}

interface HUDState {
  characterId: string;
  health: number;
  energy: number;
  level: number;
  shards: number;
  currentRealm: string;
  fps: number;
  isDarkMode: boolean;
}

export const HUD: React.FC<HUDProps> = ({ onPauseGame }) => {
  const [hudState, setHudState] = useState<HUDState>({
    characterId: 'ash',
    health: 100,
    energy: 100,
    level: 1,
    shards: 0,
    currentRealm: 'ash_gate',
    fps: 60,
    isDarkMode: true,
  });

  const [targetHealth, setTargetHealth] = useState(0);
  const [targetMaxHealth, setTargetMaxHealth] = useState(100);

  useEffect(() => {
    // Subscribe to game state changes
    gameEvents.subscribe('character_switched', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        characterId: data.characterId,
      }));
    });

    gameEvents.subscribe('health_changed', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        health: data.health,
      }));
    });

    gameEvents.subscribe('energy_changed', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        energy: data.energy,
      }));
    });

    gameEvents.subscribe('level_changed', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        level: data.level,
      }));
    });

    gameEvents.subscribe('shards_changed', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        shards: data.shards,
      }));
    });

    gameEvents.subscribe('realm_switched', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        currentRealm: data.realmId,
      }));
    });

    gameEvents.subscribe('fps_changed', (data: any) => {
      setHudState((prev) => ({
        ...prev,
        fps: data.fps,
      }));
    });

    gameEvents.subscribe('enemy_targeted', (data: any) => {
      setTargetHealth(data.health);
      setTargetMaxHealth(data.maxHealth);
    });

    gameEvents.subscribe('enemy_defeated', () => {
      setTargetHealth(0);
    });

    // Initial state
    const state = gameState.getState();
    setHudState((prev) => ({
      ...prev,
      health: state.playerState.health,
      energy: state.playerState.energy,
      level: state.playerState.level,
      shards: state.playerState.shards,
      characterId: state.currentCharacter,
      currentRealm: state.currentRealm,
    }));

    // Keyboard shortcut for pause
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Escape') {
        onPauseGame();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      gameEvents.clear();
    };
  }, [onPauseGame]);

  return (
    <div className="hud fade-in">
      {/* Top Left - Character Info */}
      <div className="hud-top-left">
        <CharacterInfoPanel
          characterId={hudState.characterId}
          health={hudState.health}
          energy={hudState.energy}
          level={hudState.level}
          shards={hudState.shards}
        />
      </div>

      {/* Top Right - Minimap */}
      <div className="hud-top-right">
        <Minimap realm={hudState.currentRealm} />
      </div>

      {/* Bottom Left - Quest Tracker */}
      <div className="hud-bottom-left">
        <QuestTracker />
      </div>

      {/* Bottom Center - Ability Bar */}
      <div className="hud-bottom-center">
        <AbilityBar characterId={hudState.characterId} />
      </div>

      {/* Bottom Right - Debug Info & Buttons */}
      <div className="hud-bottom-right">
        <div style={{ fontSize: '0.9rem', color: '#888' }}>
          FPS: {hudState.fps.toFixed(0)} | Realm: {hudState.currentRealm}
        </div>
        <button
          className="btn btn-primary"
          onClick={onPauseGame}
          style={{ marginTop: '10px', width: '100px' }}
        >
          Pause (ESC)
        </button>
      </div>

      {/* Enemy Target Health Bar */}
      {targetMaxHealth > 0 && (
        <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translateX(-50%)' }}>
          <EnemyHealthBar health={targetHealth} maxHealth={targetMaxHealth} />
        </div>
      )}

      {/* FPS & Performance Stats */}
      <div className="status-text">
        {hudState.fps.toFixed(0)} FPS | {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};
