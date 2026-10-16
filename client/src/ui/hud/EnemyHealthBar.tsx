/**
 * Enemy Health Bar - شريط صحة العدو
 * يعرض صحة العدو المستهدف أعلى الشاشة
 */

import React from 'react';

export interface EnemyHealthBarProps {
  health: number;
  maxHealth: number;
}

export const EnemyHealthBar: React.FC<EnemyHealthBarProps> = ({ health, maxHealth }) => {
  const healthPercent = (health / maxHealth) * 100;

  const getColor = () => {
    if (healthPercent > 70) return '#4ade80';
    if (healthPercent > 40) return '#fbbf24';
    return '#ff6b6b';
  };

  return (
    <div
      style={{
        background: 'rgba(0, 0, 0, 0.7)',
        border: '2px solid #ffa94d',
        borderRadius: '4px',
        padding: '8px 12px',
        minWidth: '250px',
        backdropFilter: 'blur(10px)',
      }}
    >
      <div
        style={{
          fontSize: '0.9rem',
          color: '#ffa94d',
          marginBottom: '6px',
          fontWeight: 'bold',
        }}
      >
        Enemy Health
      </div>
      <div
        style={{
          width: '100%',
          height: '20px',
          background: 'rgba(0, 0, 0, 0.5)',
          border: '1px solid rgba(255, 169, 77, 0.3)',
          borderRadius: '3px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${healthPercent}%`,
            background: getColor(),
            transition: 'width 0.1s ease',
            position: 'relative',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)',
              animation: 'shimmer 2s infinite',
            }}
          />
        </div>
      </div>
      <div
        style={{
          fontSize: '0.75rem',
          color: '#888',
          marginTop: '4px',
          textAlign: 'right',
        }}
      >
        {Math.floor(health)}/{maxHealth}
      </div>
    </div>
  );
};
