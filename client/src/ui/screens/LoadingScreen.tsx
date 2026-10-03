/**
 * Loading Screen - شاشة التحميل
 * يعرض تقدم التهيئة أثناء بدء اللعبة
 */

import React from 'react';

export interface LoadingScreenProps {
  progress: number;
  error?: string;
}

const LOADING_TIPS = [
  'Prepare your strategy...',
  'Three realms await...',
  'Master the elements...',
  'Discover hidden secrets...',
  'Challenge the bosses...',
  'Become a legend...',
];

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ progress, error }) => {
  const tip = LOADING_TIPS[Math.floor(Math.random() * LOADING_TIPS.length)];

  return (
    <div className="loading-screen">
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#ffa94d', marginBottom: '1rem' }}>
          Naris Realms
        </h1>
        <p style={{ fontSize: '1rem', color: '#888' }}>سجلات الرماد</p>
      </div>

      <div className="loading-spinner" />

      <div style={{ textAlign: 'center', gap: '1rem', display: 'flex', flexDirection: 'column' }}>
        <div className="loading-text">{tip}</div>
        <div className="loading-progress">
          <div
            className="loading-progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div style={{ fontSize: '0.9rem', color: '#888' }}>
          {Math.floor(progress)}% - Loading Game Engine
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ Error: {error}
        </div>
      )}
    </div>
  );
};
