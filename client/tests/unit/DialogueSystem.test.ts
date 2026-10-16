/**
 * Dialogue System Tests - اختبارات نظام الحوار
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { DialogueSystem, dialogueSystem, DialogueNode } from '../../src/game/core/DialogueSystem';

describe('DialogueSystem', () => {
  beforeEach(() => {
    dialogueSystem.skipDialogue();
  });

  it('should be a singleton', () => {
    const instance1 = DialogueSystem.getInstance();
    const instance2 = DialogueSystem.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should register a dialogue', () => {
    const dialogue: DialogueNode = {
      id: 'test_dialogue',
      lines: [
        {
          id: 'line1',
          characterId: 'char1',
          text: 'Hello',
          language: 'en',
          duration: 1000,
        },
      ],
      choices: [],
    };

    dialogueSystem.registerDialogue(dialogue);
    const retrieved = dialogueSystem.getDialogue('test_dialogue');

    expect(retrieved).toBeDefined();
    expect(retrieved?.lines.length).toBe(1);
  });

  it('should start dialogue', (done) => {
    const dialogue: DialogueNode = {
      id: 'test_dialogue_2',
      lines: [
        {
          id: 'line1',
          characterId: 'char1',
          text: 'Hello',
          language: 'en',
          duration: 100,
        },
      ],
      choices: [],
    };

    dialogueSystem.registerDialogue(dialogue);
    const started = dialogueSystem.startDialogue('test_dialogue_2');

    expect(started).toBe(true);
    expect(dialogueSystem.isDialoguePlaying()).toBe(true);

    setTimeout(() => {
      expect(dialogueSystem.isDialoguePlaying()).toBe(false);
      done();
    }, 200);
  });

  it('should get current line', () => {
    const dialogue: DialogueNode = {
      id: 'test_dialogue_3',
      lines: [
        {
          id: 'line1',
          characterId: 'char1',
          text: 'Test',
          language: 'en',
          duration: 1000,
        },
      ],
      choices: [],
    };

    dialogueSystem.registerDialogue(dialogue);
    dialogueSystem.startDialogue('test_dialogue_3');

    const current = dialogueSystem.getCurrentLine();
    expect(current).toBeDefined();
    expect(current?.text).toBe('Test');

    dialogueSystem.skipDialogue();
  });

  it('should get current choices', () => {
    const dialogue: DialogueNode = {
      id: 'test_dialogue_4',
      lines: [],
      choices: [
        {
          id: 'choice1',
          text: 'Option 1',
          nextLineId: 'line2',
        },
      ],
    };

    dialogueSystem.registerDialogue(dialogue);
    dialogueSystem.startDialogue('test_dialogue_4');

    const choices = dialogueSystem.getCurrentChoices();
    expect(choices.length).toBeGreaterThan(0);

    dialogueSystem.skipDialogue();
  });

  it('should skip dialogue', () => {
    const dialogue: DialogueNode = {
      id: 'test_dialogue_5',
      lines: [
        {
          id: 'line1',
          characterId: 'char1',
          text: 'Test',
          language: 'en',
          duration: 5000,
        },
      ],
      choices: [],
    };

    dialogueSystem.registerDialogue(dialogue);
    dialogueSystem.startDialogue('test_dialogue_5');
    dialogueSystem.skipDialogue();

    expect(dialogueSystem.isDialoguePlaying()).toBe(false);
  });
});
