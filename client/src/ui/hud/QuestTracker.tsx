/**
 * Quest Tracker - متتبع المهام
 * يعرض المهام النشطة وتقدم أهدافها
 */

import React, { useEffect, useState } from 'react';
import { questSystem } from '../../game/core/QuestSystem';
import { gameEvents } from '../../game/core/EventSystem';

interface QuestDisplay {
  questId: string;
  title: string;
  progress: number;
  objectives: Array<{
    id: string;
    description: string;
    completed: boolean;
    current?: number;
    target?: number;
  }>;
}

export const QuestTracker: React.FC = () => {
  const [quests, setQuests] = useState<QuestDisplay[]>([]);
  const [expandedQuestId, setExpandedQuestId] = useState<string | null>(null);

  useEffect(() => {
    const updateQuests = () => {
      const activeQuests = questSystem.getActiveQuests();
      const displayQuests: QuestDisplay[] = activeQuests.map((tracker) => ({
        questId: tracker.questId,
        title: tracker.quest.title,
        progress: tracker.progress,
        objectives: tracker.quest.objectives.map((obj) => {
          const progress = tracker.objectives.get(obj.id) || 0;
          return {
            id: obj.id,
            description: obj.description,
            completed: progress >= 100,
            current: Math.floor(progress),
            target: obj.targetCount,
          };
        }),
      }));

      setQuests(displayQuests);
    };

    updateQuests();

    // Subscribe to quest updates
    gameEvents.subscribe('quest_started', updateQuests);
    gameEvents.subscribe('quest_completed', updateQuests);
    gameEvents.subscribe('quest_failed', updateQuests);
    gameEvents.subscribe('objective_updated', updateQuests);

    return () => {
      gameEvents.unsubscribe('quest_started');
      gameEvents.unsubscribe('quest_completed');
      gameEvents.unsubscribe('quest_failed');
      gameEvents.unsubscribe('objective_updated');
    };
  }, []);

  if (quests.length === 0) {
    return (
      <div className="quest-tracker">
        <div className="quest-title">No Active Quests</div>
        <div style={{ fontSize: '0.85rem', color: '#888' }}>Accept a quest to get started</div>
      </div>
    );
  }

  return (
    <div className="quest-tracker">
      {quests.map((quest) => (
        <div
          key={quest.questId}
          style={{
            marginBottom: '12px',
            paddingBottom: '12px',
            borderBottom: '1px solid rgba(255, 169, 77, 0.2)',
            cursor: 'pointer',
          }}
          onClick={() =>
            setExpandedQuestId(
              expandedQuestId === quest.questId ? null : quest.questId
            )
          }
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="quest-title">{quest.title}</div>
            <span style={{ color: '#888', fontSize: '0.8rem' }}>{Math.floor(quest.progress)}%</span>
          </div>

          {/* Progress Bar */}
          <div
            style={{
              width: '100%',
              height: '4px',
              background: 'rgba(255, 169, 77, 0.2)',
              borderRadius: '2px',
              overflow: 'hidden',
              marginTop: '4px',
            }}
          >
            <div
              style={{
                width: `${quest.progress}%`,
                height: '100%',
                background: '#ffa94d',
                transition: 'width 0.3s ease',
              }}
            />
          </div>

          {/* Objectives (Expanded) */}
          {expandedQuestId === quest.questId && (
            <div style={{ marginTop: '8px' }}>
              {quest.objectives.map((obj) => (
                <div key={obj.id} className="quest-objective">
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <span style={{ color: obj.completed ? '#4ade80' : '#fbbf24' }}>
                      {obj.completed ? '✓' : '○'}
                    </span>
                    <span>{obj.description}</span>
                  </div>
                  {obj.target !== undefined && obj.current !== undefined && (
                    <div
                      style={{
                        fontSize: '0.75rem',
                        color: '#888',
                        marginTop: '2px',
                        marginLeft: '20px',
                      }}
                    >
                      {obj.current}/{obj.target}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
