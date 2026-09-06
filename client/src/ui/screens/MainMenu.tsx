/**
 * Main Menu Screen - القائمة الرئيسية
 * يعرض خيارات اللعبة الرئيسية
 */

import React from 'react';

export interface MainMenuProps {
  onStartGame: () => void;
}

export const MainMenu: React.FC<MainMenuProps> = ({ onStartGame }) => {
  return (
    <div className="main-menu">
      <div>
        <h1 className="menu-title">Naris Realms</h1>
        <p className="menu-subtitle">سجلات الرماد</p>
      </div>

      <div>
        <p style={{ fontSize: '0.95rem', color: '#888', maxWidth: '600px', textAlign: 'center' }}>
          Embark on an epic journey through three interconnected realms. Master three powerful
          characters, defeat formidable bosses, and uncover the secrets of the Ash Records.
        </p>
      </div>

      <div className="menu-buttons">
        <button className="btn btn-primary" onClick={onStartGame}>
          🎮 Start Game
        </button>
        <button className="btn" onClick={() => alert('Settings coming soon!')}>
          ⚙️ Settings
        </button>
        <button className="btn" onClick={() => alert('Guide coming soon!')}>
          📖 How to Play
        </button>
        <button className="btn" onClick={() => alert('Credits coming soon!')}>
          ⭐ Credits
        </button>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.85rem', color: '#888' }}>
        <p>v1.0.0 | React 19 + Babylon.js 8.0</p>
        <p style={{ marginTop: '0.5rem' }}>Press ESC during gameplay to pause</p>
      </div>
    </div>
  );
};
