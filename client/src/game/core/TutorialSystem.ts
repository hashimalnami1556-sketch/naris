/**
 * Tutorial System - نظام البرنامج التعليمي
 * إدارة التلميحات والدروس الأساسية
 */

import { EventSystem, gameEvents } from './EventSystem';

export interface Hint {
  id: string;
  title: string;
  description: string;
  action: string;
  showOnce: boolean;
  shown: boolean;
  triggerEvent?: string;
}

export interface TutorialStep {
  id: string;
  title: string;
  hints: Hint[];
  completed: boolean;
  order: number;
}

export class TutorialSystem {
  private static instance: TutorialSystem;
  private steps: Map<string, TutorialStep> = new Map();
  private hints: Map<string, Hint> = new Map();
  private currentStepId: string | null = null;
  private shownHints: Set<string> = new Set();
  private isEnabled: boolean = true;

  private constructor() {}

  static getInstance(): TutorialSystem {
    if (!TutorialSystem.instance) {
      TutorialSystem.instance = new TutorialSystem();
    }
    return TutorialSystem.instance;
  }

  /**
   * تسجيل خطوة برنامج تعليمي
   */
  registerStep(step: TutorialStep): void {
    this.steps.set(step.id, step);

    // تسجيل الرموز في هذه الخطوة
    step.hints.forEach((hint) => {
      this.hints.set(hint.id, hint);
    });
  }

  /**
   * الانتقال إلى خطوة
   */
  goToStep(stepId: string): boolean {
    const step = this.steps.get(stepId);
    if (!step) return false;

    this.currentStepId = stepId;
    gameEvents.emit('tutorial_step_started', { stepId, step });

    console.log(`✓ Tutorial step started: ${step.title}`);
    return true;
  }

  /**
   * إكمال الخطوة الحالية
   */
  completeCurrentStep(): boolean {
    if (!this.currentStepId) return false;

    const step = this.steps.get(this.currentStepId)!;
    step.completed = true;

    gameEvents.emit('tutorial_step_completed', { stepId: this.currentStepId });
    console.log(`✓ Tutorial step completed: ${step.title}`);

    // الانتقال إلى الخطوة التالية
    const nextStep = this.getNextStep();
    if (nextStep) {
      this.goToStep(nextStep.id);
    } else {
      this.currentStepId = null;
      gameEvents.emit('tutorial_completed', {});
    }

    return true;
  }

  /**
   * الحصول على الخطوة التالية
   */
  getNextStep(): TutorialStep | null {
    const steps = Array.from(this.steps.values()).sort((a, b) => a.order - b.order);

    for (const step of steps) {
      if (!step.completed) {
        return step;
      }
    }

    return null;
  }

  /**
   * عرض تلميح
   */
  showHint(hintId: string): boolean {
    const hint = this.hints.get(hintId);
    if (!hint || !this.isEnabled) return false;

    if (hint.showOnce && this.shownHints.has(hintId)) {
      return false;
    }

    this.shownHints.add(hintId);
    hint.shown = true;

    gameEvents.emit('hint_shown', { hintId, hint });
    console.log(`✓ Hint shown: ${hint.title}`);

    return true;
  }

  /**
   * الحصول على التلميحات الحالية
   */
  getCurrentHints(): Hint[] {
    if (!this.currentStepId) return [];

    const step = this.steps.get(this.currentStepId);
    return step ? step.hints : [];
  }

  /**
   * تفعيل/تعطيل البرنامج التعليمي
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;

    if (enabled) {
      gameEvents.emit('tutorial_enabled', {});
      console.log('✓ Tutorial enabled');
    } else {
      gameEvents.emit('tutorial_disabled', {});
      console.log('✓ Tutorial disabled');
    }
  }

  /**
   * هل البرنامج التعليمي مفعل
   */
  isEnabledState(): boolean {
    return this.isEnabled;
  }

  /**
   * إعادة تعيين البرنامج التعليمي
   */
  reset(): void {
    this.steps.forEach((step) => {
      step.completed = false;
    });
    this.shownHints.clear();
    this.currentStepId = null;

    gameEvents.emit('tutorial_reset', {});
    console.log('✓ Tutorial reset');
  }

  /**
   * الحصول على تقدم البرنامج التعليمي
   */
  getProgress(): { completed: number; total: number; percentage: number } {
    const total = this.steps.size;
    const completed = Array.from(this.steps.values()).filter((s) => s.completed).length;

    return {
      completed,
      total,
      percentage: total > 0 ? (completed / total) * 100 : 0,
    };
  }
}

export const tutorialSystem = TutorialSystem.getInstance();
