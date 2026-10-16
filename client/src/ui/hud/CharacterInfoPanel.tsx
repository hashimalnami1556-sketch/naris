/**
 * Character Info Panel - لوحة معلومات الشخصية
 * يعرض صحة اللاعب والطاقة والمستوى والموارد
 */

import React from 'react';

export interface CharacterInfoPanelProps {
  characterId: string;
  health: number;
  energy: number;
  level: number;
  shards: number;
}

const CHARACTER_NAMES: Record<string, string> = {
  ash: 'Ash — الرماد',
  rune: 'Rune — الرون',
  kor: 'Kor — كور',
};

const CHARACTER_ICONS: Record<string, string> = {
  ash: '⚡',
  rune: '✨',
  kor: '💪',
};

export const CharacterInfoPanel: React.FC<CharacterInfoPanelProps> = ({
  characterId,
  health,
  energy,
  level,
  shards,
}) => {
  const maxHealth = 100;
  const maxEnergy = 100;
  const healthPercent = (health / maxHealth) * 100;
  const energyPercent = (energy / maxEnergy) * 100;

  // Color coding based on health
  const getHealthColor = () => {
    if (health > 70) return '#4ade80'; // green
    if (health > 40) return '#fbbf24'; // yellow
    return '#ff6b6b'; // red
  };

  const getEnergyColor = () => {
    if (energy > 70) return '#3b82f6'; // blue
    if (energy > 40) return '#fbbf24'; // yellow
    return '#ff6b6b'; // red
  };

  return (
    <div className="character-info slide-in">
      <div className="character-name">
        {CHARACTER_ICONS[characterId] || '⚔️'} {CHARACTER_NAMES[characterId] || characterId}
      </div>
      <div className="character-level">Level {level}</div>

      {/* Health Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>Health</span>
          <span>{Math.floor(health)}/{maxHealth}</span>
        </div>
        <div className="stat-bar-container">
          <div
            className="stat-bar-fill"
            style={{
              width: `${healthPercent}%`,
              background: getHealthColor(),
            }}
          />
        </div>
      </div>

      {/* Energy Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>Energy</span>
          <span>{Math.floor(energy)}/{maxEnergy}</span>
        </div>
        <div className="stat-bar-container">
          <div
            className="stat-bar-fill"
            style={{
              width: `${energyPercent}%`,
              background: getEnergyColor(),
            }}
          />
        </div>
      </div>

      {/* Shards Display */}
      <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '1.2rem' }}>💎</span>
        <span style={{ color: '#fbbf24', fontWeight: 'bold' }}>{shards}</span>
        <span style={{ fontSize: '0.85rem', color: '#888' }}>Shards</span>
      </div>
    </div>
  );
};
