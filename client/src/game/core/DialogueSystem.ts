/**
 * Dialogue System - نظام الحوار
 * إدارة حوارات الشخصيات والخيارات
 */

import { EventSystem, gameEvents } from './EventSystem';

export interface DialogueLine {
  id: string;
  characterId: string;
  text: string;
  language: 'en' | 'ar';
  emotion?: 'neutral' | 'happy' | 'sad' | 'angry' | 'surprised';
  duration: number; // ms
}

export interface DialogueChoice {
  id: string;
  text: string;
  nextLineId: string;
  condition?: () => boolean;
}

export interface DialogueNode {
  id: string;
  lines: DialogueLine[];
  choices: DialogueChoice[];
  onComplete?: () => void;
}

export class DialogueSystem {
  private static instance: DialogueSystem;
  private dialogues: Map<string, DialogueNode> = new Map();
  private currentDialogueId: string | null = null;
  private currentLineIndex: number = 0;
  private isPlaying: boolean = false;
  private lineTimer: NodeJS.Timeout | null = null;

  private constructor() {}

  static getInstance(): DialogueSystem {
    if (!DialogueSystem.instance) {
      DialogueSystem.instance = new DialogueSystem();
    }
    return DialogueSystem.instance;
  }

  /**
   * تسجيل حوار
   */
  registerDialogue(dialogue: DialogueNode): void {
    this.dialogues.set(dialogue.id, dialogue);
  }

  /**
   * الحصول على حوار
   */
  getDialogue(dialogueId: string): DialogueNode | undefined {
    return this.dialogues.get(dialogueId);
  }

  /**
   * بدء حوار
   */
  startDialogue(dialogueId: string): boolean {
    const dialogue = this.dialogues.get(dialogueId);
    if (!dialogue || this.isPlaying) return false;

    this.currentDialogueId = dialogueId;
    this.currentLineIndex = 0;
    this.isPlaying = true;

    gameEvents.emit('dialogue_started', { dialogueId });
    this.playNextLine();

    return true;
  }

  /**
   * تشغيل السطر التالي
   */
  playNextLine(): void {
    if (!this.currentDialogueId) return;

    const dialogue = this.dialogues.get(this.currentDialogueId)!;
    if (this.currentLineIndex >= dialogue.lines.length) {
      this.endDialogue();
      return;
    }

    const line = dialogue.lines[this.currentLineIndex];

    if (this.lineTimer) {
      clearTimeout(this.lineTimer);
    }

    gameEvents.emit('dialogue_line_displayed', {
      dialogueId: this.currentDialogueId,
      lineIndex: this.currentLineIndex,
      line,
    });

    this.lineTimer = setTimeout(() => {
      this.currentLineIndex++;
      this.playNextLine();
    }, line.duration);
  }

  /**
   * إنهاء الحوار
   */
  endDialogue(): void {
    if (!this.currentDialogueId) return;

    const dialogue = this.dialogues.get(this.currentDialogueId)!;

    if (this.lineTimer) {
      clearTimeout(this.lineTimer);
      this.lineTimer = null;
    }

    if (dialogue.onComplete) {
      dialogue.onComplete();
    }

    gameEvents.emit('dialogue_ended', { dialogueId: this.currentDialogueId });
    console.log(`✓ Dialogue ended: ${this.currentDialogueId}`);

    this.currentDialogueId = null;
    this.currentLineIndex = 0;
    this.isPlaying = false;
  }

  /**
   * الحصول على الخيارات الحالية
   */
  getCurrentChoices(): DialogueChoice[] {
    if (!this.currentDialogueId) return [];

    const dialogue = this.dialogues.get(this.currentDialogueId)!;
    return dialogue.choices.filter((choice) => !choice.condition || choice.condition());
  }

  /**
   * اختيار خيار
   */
  selectChoice(choiceId: string): void {
    const choices = this.getCurrentChoices();
    const choice = choices.find((c) => c.id === choiceId);

    if (!choice) return;

    gameEvents.emit('dialogue_choice_selected', {
      dialogueId: this.currentDialogueId,
      choiceId,
    });

    // يمكن الانتقال إلى سطر آخر بناءً على الخيار
    if (choice.nextLineId) {
      // التعامل مع الانتقال
      console.log(`✓ Choice selected: moving to ${choice.nextLineId}`);
    }
  }

  /**
   * هل الحوار قيد التشغيل
   */
  isDialoguePlaying(): boolean {
    return this.isPlaying;
  }

  /**
   * إيقاف الحوار
   */
  skipDialogue(): void {
    if (!this.isPlaying) return;

    if (this.lineTimer) {
      clearTimeout(this.lineTimer);
    }

    this.endDialogue();
  }

  /**
   * الحصول على السطر الحالي
   */
  getCurrentLine(): DialogueLine | null {
    if (!this.currentDialogueId) return null;

    const dialogue = this.dialogues.get(this.currentDialogueId)!;
    return dialogue.lines[this.currentLineIndex] || null;
  }
}

export const dialogueSystem = DialogueSystem.getInstance();
