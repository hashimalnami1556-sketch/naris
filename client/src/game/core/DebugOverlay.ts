/**
 * Debug Overlay - طبقة تصحيح الأخطاء
 * عرض معلومات التصحيح على الشاشة
 */

import { EventSystem, gameEvents } from './EventSystem';
import { PerformanceMonitor, performanceMonitor } from './PerformanceMonitor';

export interface DebugInfo {
  [key: string]: any;
}

export class DebugOverlay {
  private static instance: DebugOverlay;
  private debugInfo: Map<string, any> = new Map();
  private isVisible: boolean = false;
  private overlayElement: HTMLElement | null = null;
  private updateInterval: NodeJS.Timeout | null = null;

  private constructor() {}

  static getInstance(): DebugOverlay {
    if (!DebugOverlay.instance) {
      DebugOverlay.instance = new DebugOverlay();
    }
    return DebugOverlay.instance;
  }

  /**
   * إظهار طبقة التصحيح
   */
  show(): void {
    if (this.isVisible) return;

    this.isVisible = true;
    this.createOverlayElement();
    this.startUpdating();

    gameEvents.emit('debug_overlay_shown', {});
    console.log('✓ Debug Overlay shown');
  }

  /**
   * إخفاء طبقة التصحيح
   */
  hide(): void {
    if (!this.isVisible) return;

    this.isVisible = false;
    this.removeOverlayElement();
    this.stopUpdating();

    gameEvents.emit('debug_overlay_hidden', {});
    console.log('✓ Debug Overlay hidden');
  }

  /**
   * تبديل طبقة التصحيح
   */
  toggle(): void {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }

  /**
   * إضافة معلومة تصحيح
   */
  addDebugInfo(key: string, value: any): void {
    this.debugInfo.set(key, value);
  }

  /**
   * إزالة معلومة تصحيح
   */
  removeDebugInfo(key: string): void {
    this.debugInfo.delete(key);
  }

  /**
   * تحديث معلومة تصحيح
   */
  updateDebugInfo(key: string, value: any): void {
    this.debugInfo.set(key, value);
  }

  /**
   * الحصول على معلومات التصحيح
   */
  getDebugInfo(): DebugInfo {
    const result: DebugInfo = {};
    this.debugInfo.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }

  /**
   * مسح معلومات التصحيح
   */
  clearDebugInfo(): void {
    this.debugInfo.clear();
  }

  /**
   * إنشاء عنصر طبقة التصحيح
   */
  private createOverlayElement(): void {
    if (this.overlayElement) return;

    const overlay = document.createElement('div');
    overlay.id = 'debug-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.8);
      color: #00ff00;
      font-family: monospace;
      font-size: 12px;
      padding: 10px;
      border: 1px solid #00ff00;
      max-width: 400px;
      max-height: 400px;
      overflow-y: auto;
      z-index: 10000;
      pointer-events: none;
    `;

    document.body.appendChild(overlay);
    this.overlayElement = overlay;
  }

  /**
   * إزالة عنصر طبقة التصحيح
   */
  private removeOverlayElement(): void {
    if (this.overlayElement) {
      this.overlayElement.remove();
      this.overlayElement = null;
    }
  }

  /**
   * بدء التحديث
   */
  private startUpdating(): void {
    if (this.updateInterval) return;

    this.updateInterval = setInterval(() => {
      this.updateOverlay();
    }, 100);
  }

  /**
   * إيقاف التحديث
   */
  private stopUpdating(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  /**
   * تحديث طبقة التصحيح
   */
  private updateOverlay(): void {
    if (!this.overlayElement || !this.isVisible) return;

    const metrics = performanceMonitor.getMetrics();

    let content = '<div style="color: #ffff00; font-weight: bold; margin-bottom: 8px;">DEBUG INFO</div>';

    // أداء
    content += `<div>FPS: ${metrics.fps.toFixed(1)}</div>`;
    content += `<div>Frame: ${metrics.frameTime.toFixed(2)}ms</div>`;
    content += `<div>Memory: ${metrics.memoryUsed.toFixed(1)}MB</div>`;
    content += '<div style="margin-top: 8px; border-top: 1px solid #00ff00; padding-top: 8px;"></div>';

    // معلومات التصحيح المخصصة
    this.debugInfo.forEach((value, key) => {
      let displayValue = value;
      if (typeof value === 'object') {
        displayValue = JSON.stringify(value).substring(0, 50);
      }
      content += `<div>${key}: ${displayValue}</div>`;
    });

    this.overlayElement.innerHTML = content;
  }
}

export const debugOverlay = DebugOverlay.getInstance();
