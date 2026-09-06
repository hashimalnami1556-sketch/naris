/**
 * Ability Bar - شريط القدرات
 * يعرض القدرات المتاحة للشخصية مع مفاتيح لوحة المفاتيح
 */

import React, { useEffect, useState } from 'react';
import { gameEvents } from '../../game/core/EventSystem';

export interface AbilityBarProps {
  characterId: string;
}

interface Ability {
  id: string;
  name: string;
  icon: string;
  key: string;
  cooldown: number;
  maxCooldown: number;
}

const CHARACTER_ABILITIES: Record<string, Ability[]> = {
  ash: [
    { id: 'slash', name: 'Slash', icon: '⚡', key: 'Z', cooldown: 0, maxCooldown: 0.5 },
    { id: 'lightning_strike', name: 'Lightning Strike', icon: '🔱', key: 'X', cooldown: 0, maxCooldown: 3 },
    { id: 'chain_lightning', name: 'Chain Lightning', icon: '⚙️', key: 'C', cooldown: 0, maxCooldown: 5 },
  ],
  rune: [
    { id: 'arcane_bolt', name: 'Arcane Bolt', icon: '✨', key: 'Z', cooldown: 0, maxCooldown: 1 },
    { id: 'frost_nova', name: 'Frost Nova', icon: '❄️', key: 'X', cooldown: 0, maxCooldown: 4 },
    { id: 'time_warp', name: 'Time Warp', icon: '⏰', key: 'C', cooldown: 0, maxCooldown: 8 },
  ],
  kor: [
    { id: 'savage_strike', name: 'Savage Strike', icon: '💪', key: 'Z', cooldown: 0, maxCooldown: 0.3 },
    { id: 'earthquake', name: 'Earthquake', icon: '🌊', key: 'X', cooldown: 0, maxCooldown: 4 },
    { id: 'berserker_rage', name: 'Berserker Rage', icon: '🔥', key: 'C', cooldown: 0, maxCooldown: 6 },
  ],
};

export const AbilityBar: React.FC<AbilityBarProps> = ({ characterId }) => {
  const [abilities, setAbilities] = useState<Ability[]>(
    CHARACTER_ABILITIES[characterId] || CHARACTER_ABILITIES['ash']
  );

  useEffect(() => {
    // Update abilities based on character
    setAbilities(CHARACTER_ABILITIES[characterId] || CHARACTER_ABILITIES['ash']);

    // Subscribe to ability cooldown updates
    gameEvents.subscribe('ability_used', (data: any) => {
      setAbilities((prev) =>
        prev.map((ability) =>
          ability.id === data.abilityId
            ? { ...ability, cooldown: ability.maxCooldown }
            : ability
        )
      );
    });

    // Cooldown timer
    const cooldownTimer = setInterval(() => {
      setAbilities((prev) =>
        prev.map((ability) => ({
          ...ability,
          cooldown: Math.max(0, ability.cooldown - 0.016), // ~60 FPS
        }))
      );
    }, 16);

    return () => {
      clearInterval(cooldownTimer);
    };
  }, [characterId]);

  const handleAbilityClick = (abilityId: string) => {
    gameEvents.emit('ability_triggered', { abilityId });
  };

  return (
    <div className="ability-bar">
      {abilities.map((ability) => {
        const cooldownPercent = (ability.cooldown / ability.maxCooldown) * 100;
        const isOnCooldown = ability.cooldown > 0;

        return (
          <div
            key={ability.id}
            className="ability-slot"
            onClick={() => !isOnCooldown && handleAbilityClick(ability.id)}
            title={ability.name}
            style={{
              opacity: isOnCooldown ? 0.5 : 1,
              cursor: isOnCooldown ? 'not-allowed' : 'pointer',
            }}
          >
            <span style={{ fontSize: '1.3rem' }}>{ability.icon}</span>
            <span className="ability-key">{ability.key}</span>
            {isOnCooldown && (
              <span className="ability-cooldown">{ability.cooldown.toFixed(1)}s</span>
            )}
          </div>
        );
      })}
    </div>
  );
};
