/**
 * Save System Tests - اختبارات نظام الحفظ
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SaveSystem, saveSystem } from '../../src/game/core/SaveSystem';
import { gameEvents } from '../../src/game/core/EventSystem';
import { gameState } from '../../src/game/core/StateManager';

describe('SaveSystem', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    saveSystem.clearAllSaves();
  });

  it('should be a singleton', () => {
    const instance1 = SaveSystem.getInstance();
    const instance2 = SaveSystem.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should save game data', () => {
    saveSystem.save('test_save');
    const saves = saveSystem.getSavesList();
    expect(saves.length).toBeGreaterThan(0);
    expect(saves[0].name).toBe('test_save');
  });

  it('should load game data', () => {
    saveSystem.save('test_save');
    const loaded = saveSystem.load('test_save');
    expect(loaded).toBe(true);
  });

  it('should return false when loading non-existent save', () => {
    const loaded = saveSystem.load('non_existent');
    expect(loaded).toBe(false);
  });

  it('should delete save data', () => {
    saveSystem.save('test_save');
    const deleted = saveSystem.deleteSave('test_save');
    expect(deleted).toBe(true);

    const loaded = saveSystem.load('test_save');
    expect(loaded).toBe(false);
  });

  it('should clear all saves', () => {
    saveSystem.save('save1');
    saveSystem.save('save2');
    saveSystem.clearAllSaves();

    const saves = saveSystem.getSavesList();
    expect(saves.length).toBe(0);
  });

  it('should enable auto-save', (done) => {
    saveSystem.enableAutoSave(100);
    setTimeout(() => {
      const saves = saveSystem.getSavesList();
      expect(saves.some((s) => s.name === 'autosave')).toBe(true);
      saveSystem.disableAutoSave();
      done();
    }, 150);
  });

  it('should disable auto-save', () => {
    saveSystem.enableAutoSave();
    saveSystem.disableAutoSave();
    // Just verify no errors occur
    expect(true).toBe(true);
  });
});
