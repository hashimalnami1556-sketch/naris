/**
 * Game Over Screen - شاشة نهاية اللعبة
 * يعرض النتائج النهائية والخيارات
 */

import React, { useState, useEffect } from 'react';
import { gameState } from '../../game/core/StateManager';

export interface GameOverScreenProps {
  onResetGame: () => void;
}

interface Stats {
  level: number;
  shards: number;
  questsCompleted: number;
  enemiesDefeated: number;
  playtime: string;
}

export const GameOverScreen: React.FC<GameOverScreenProps> = ({ onResetGame }) => {
  const [stats, setStats] = useState<Stats>({
    level: 1,
    shards: 0,
    questsCompleted: 0,
    enemiesDefeated: 0,
    playtime: '0:00',
  });

  useEffect(() => {
    const gameState_data = gameState.getState();
    setStats({
      level: gameState_data.playerState.level,
      shards: gameState_data.playerState.shards,
      questsCompleted: gameState_data.playerState.questsCompleted || 0,
      enemiesDefeated: gameState_data.playerState.combatKills || 0,
      playtime: '5:32', // Placeholder
    });
  }, []);

  return (
    <div className="game-over-screen">
      <h1 className="game-over-title">GAME OVER</h1>
      <p className="game-over-subtitle">You have fallen...</p>

      <div
        style={{
          background: 'rgba(0, 0, 0, 0.7)',
          padding: '2rem',
          borderRadius: '8px',
          border: '2px solid #ffa94d',
          minWidth: '400px',
        }}
      >
        <h2 style={{ color: '#ffa94d', marginBottom: '1.5rem', textAlign: 'center' }}>
          Final Statistics
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <div style={{ color: '#888', fontSize: '0.9rem' }}>Final Level</div>
            <div style={{ color: '#ffa94d', fontSize: '1.5rem', fontWeight: 'bold' }}>
              {stats.level}
            </div>
          </div>
          <div>
            <div style={{ color: '#888', fontSize: '0.9rem' }}>Shards Collected</div>
            <div style={{ color: '#fbbf24', fontSize: '1.5rem', fontWeight: 'bold' }}>
              💎 {stats.shards}
            </div>
          </div>
          <div>
            <div style={{ color: '#888', fontSize: '0.9rem' }}>Quests Completed</div>
            <div style={{ color: '#4ade80', fontSize: '1.5rem', fontWeight: 'bold' }}>
              {stats.questsCompleted}
            </div>
          </div>
          <div>
            <div style={{ color: '#888', fontSize: '0.9rem' }}>Enemies Defeated</div>
            <div style={{ color: '#ff6b6b', fontSize: '1.5rem', fontWeight: 'bold' }}>
              {stats.enemiesDefeated}
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginBottom: '1.5rem', fontSize: '0.9rem', color: '#888' }}>
          Playtime: {stats.playtime}
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          gap: '1rem',
          marginTop: '2rem',
        }}
      >
        <button className="btn btn-primary" onClick={onResetGame}>
          🔄 Return to Menu
        </button>
      </div>
    </div>
  );
};
