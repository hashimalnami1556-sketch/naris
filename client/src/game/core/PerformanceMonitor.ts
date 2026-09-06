/**
 * Performance Monitor - مراقب الأداء
 * تتبع الأداء والإطارات والذاكرة
 */

import { EventSystem, gameEvents } from './EventSystem';

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  memoryUsed: number;
  memoryTotal: number;
  drawCalls: number;
  triangles: number;
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetrics = {
    fps: 0,
    frameTime: 0,
    memoryUsed: 0,
    memoryTotal: 0,
    drawCalls: 0,
    triangles: 0,
  };
  private frameCount: number = 0;
  private lastTime: number = Date.now();
  private updateInterval: NodeJS.Timeout | null = null;
  private isMonitoring: boolean = false;
  private frameHistory: number[] = [];
  private maxHistorySize: number = 60;

  private constructor() {}

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * بدء المراقبة
   */
  startMonitoring(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;

    this.updateInterval = setInterval(() => {
      this.updateMetrics();
    }, 1000); // تحديث كل ثانية

    gameEvents.emit('performance_monitoring_started', {});
    console.log('✓ Performance Monitoring started');
  }

  /**
   * إيقاف المراقبة
   */
  stopMonitoring(): void {
    if (!this.isMonitoring) return;

    this.isMonitoring = false;

    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    gameEvents.emit('performance_monitoring_stopped', {});
    console.log('✓ Performance Monitoring stopped');
  }

  /**
   * تسجيل إطار
   */
  recordFrame(frameTime: number): void {
    this.frameCount++;
    this.frameHistory.push(frameTime);

    if (this.frameHistory.length > this.maxHistorySize) {
      this.frameHistory.shift();
    }
  }

  /**
   * تحديث المقاييس
   */
  private updateMetrics(): void {
    const currentTime = Date.now();
    const deltaTime = (currentTime - this.lastTime) / 1000;

    if (deltaTime > 0) {
      this.metrics.fps = this.frameCount / deltaTime;
    }

    const avgFrameTime = this.frameHistory.reduce((a, b) => a + b, 0) / Math.max(1, this.frameHistory.length);
    this.metrics.frameTime = avgFrameTime;

    // معلومات الذاكرة (إن أمكن الوصول إليها)
    if ((performance as any).memory) {
      this.metrics.memoryUsed = (performance as any).memory.usedJSHeapSize / (1024 * 1024);
      this.metrics.memoryTotal = (performance as any).memory.totalJSHeapSize / (1024 * 1024);
    }

    this.frameCount = 0;
    this.lastTime = currentTime;

    gameEvents.emit('performance_metrics_updated', { metrics: this.metrics });
  }

  /**
   * الحصول على المقاييس الحالية
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * الحصول على متوسط الإطارات
   */
  getAverageFPS(): number {
    if (this.frameHistory.length === 0) return 0;
    const avgFrameTime = this.frameHistory.reduce((a, b) => a + b, 0) / this.frameHistory.length;
    return avgFrameTime > 0 ? 1000 / avgFrameTime : 0;
  }

  /**
   * الحصول على أعلى FPS
   */
  getPeakFPS(): number {
    if (this.frameHistory.length === 0) return 0;
    const minFrameTime = Math.min(...this.frameHistory);
    return minFrameTime > 0 ? 1000 / minFrameTime : 0;
  }

  /**
   * الحصول على أقل FPS
   */
  getLowestFPS(): number {
    if (this.frameHistory.length === 0) return 0;
    const maxFrameTime = Math.max(...this.frameHistory);
    return maxFrameTime > 0 ? 1000 / maxFrameTime : 0;
  }

  /**
   * هل تحت الحد الأدنى
   */
  isBelowThreshold(threshold: number = 30): boolean {
    return this.metrics.fps < threshold;
  }

  /**
   * إعادة تعيين التاريخ
   */
  resetHistory(): void {
    this.frameHistory = [];
    this.frameCount = 0;
    this.lastTime = Date.now();
  }

  /**
   * الإبلاغ عن الأداء
   */
  getPerformanceReport(): string {
    return `
FPS: ${this.metrics.fps.toFixed(2)}
Frame Time: ${this.metrics.frameTime.toFixed(2)}ms
Memory: ${this.metrics.memoryUsed.toFixed(2)}MB / ${this.metrics.memoryTotal.toFixed(2)}MB
    `.trim();
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance();
