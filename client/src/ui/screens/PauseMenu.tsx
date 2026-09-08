/**
 * Pause Menu - قائمة الإيقاف المؤقت
 * يعرض خيارات الإيقاف المؤقت والإعدادات
 */

import React, { useState } from 'react';

export interface PauseMenuProps {
  onResumeGame: () => void;
  onResetGame: () => void;
}

export const PauseMenu: React.FC<PauseMenuProps> = ({ onResumeGame, onResetGame }) => {
  const [activeTab, setActiveTab] = useState<'main' | 'settings' | 'inventory'>('main');

  return (
    <div className="pause-menu">
      <h1 className="pause-title">PAUSED</h1>

      {activeTab === 'main' && (
        <div className="pause-buttons">
          <button className="btn btn-primary" onClick={onResumeGame}>
            ▶️ Resume Game
          </button>
          <button className="btn" onClick={() => setActiveTab('settings')}>
            ⚙️ Settings
          </button>
          <button className="btn" onClick={() => setActiveTab('inventory')}>
            🎒 Inventory
          </button>
          <button className="btn" onClick={onResetGame}>
            🔄 Return to Menu
          </button>
        </div>
      )}

      {activeTab === 'settings' && (
        <div style={{ background: 'rgba(0, 0, 0, 0.7)', padding: '2rem', borderRadius: '8px' }}>
          <h2 style={{ color: '#ffa94d', marginBottom: '1.5rem' }}>Settings</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" defaultChecked />
              <span>Master Volume: 100%</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" defaultChecked />
              <span>Music: ON</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" defaultChecked />
              <span>Sound Effects: ON</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" defaultChecked />
              <span>Vibration: ON</span>
            </label>
          </div>
          <button className="btn" onClick={() => setActiveTab('main')}>
            ← Back
          </button>
        </div>
      )}

      {activeTab === 'inventory' && (
        <div style={{ background: 'rgba(0, 0, 0, 0.7)', padding: '2rem', borderRadius: '8px', minWidth: '400px' }}>
          <h2 style={{ color: '#ffa94d', marginBottom: '1.5rem' }}>Inventory</h2>
          <div style={{ fontSize: '0.95rem', color: '#888', marginBottom: '1.5rem' }}>
            <p>No items yet. Defeat enemies and complete quests to collect items.</p>
          </div>
          <button className="btn" onClick={() => setActiveTab('main')}>
            ← Back
          </button>
        </div>
      )}
    </div>
  );
};
