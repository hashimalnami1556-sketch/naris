/**
 * Performance Optimizer - محسّن الأداء
 * تحسين وتحسين أداء اللعبة والتصيير
 */

import { gameEvents } from './EventSystem';

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  memoryUsage: number;
  drawCalls: number;
  activeMeshes: number;
  texturesLoaded: number;
}

export interface PerformanceConfig {
  targetFPS: number;
  enableLOD: boolean; // Level of Detail
  enableObjectPooling: boolean;
  maxDrawCalls: number;
  meshCullDistance: number;
  enableShadows: boolean;
  shadowMapSize: number;
}

export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private metrics: PerformanceMetrics = {
    fps: 60,
    frameTime: 16.67,
    memoryUsage: 0,
    drawCalls: 0,
    activeMeshes: 0,
    texturesLoaded: 0,
  };
  private config: PerformanceConfig;
  private frameTimeHistory: number[] = [];
  private maxHistorySize: number = 120; // 2 seconds at 60fps

  private constructor() {
    this.config = {
      targetFPS: 60,
      enableLOD: true,
      enableObjectPooling: true,
      maxDrawCalls: 2000,
      meshCullDistance: 500,
      enableShadows: true,
      shadowMapSize: 2048,
    };
    console.log('⚡ PerformanceOptimizer initialized');
  }

  /**
   * الحصول على نسخة واحدة من محسّن الأداء
   */
  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  /**
   * تحديث مقاييس الأداء
   */
  updateMetrics(metrics: Partial<PerformanceMetrics>): void {
    this.metrics = { ...this.metrics, ...metrics };

    // تتبع سجل الإطار
    if (metrics.frameTime) {
      this.frameTimeHistory.push(metrics.frameTime);
      if (this.frameTimeHistory.length > this.maxHistorySize) {
        this.frameTimeHistory.shift();
      }
    }

    // تحديث FPS
    if (metrics.frameTime && metrics.frameTime > 0) {
      this.metrics.fps = 1000 / metrics.frameTime;
    }

    // بث حدث عندما تنخفض الأداء
    if (this.metrics.fps < this.config.targetFPS * 0.8) {
      gameEvents.emit('performance_warning', {
        fps: this.metrics.fps,
        targetFPS: this.config.targetFPS,
      });
    }
  }

  /**
   * الحصول على مقاييس الأداء الحالية
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * الحصول على متوسط FPS
   */
  getAverageFPS(): number {
    if (this.frameTimeHistory.length === 0) return this.metrics.fps;
    const avgFrameTime =
      this.frameTimeHistory.reduce((a, b) => a + b, 0) / this.frameTimeHistory.length;
    return 1000 / avgFrameTime;
  }

  /**
   * تكييف جودة المشهد بناءً على الأداء
   */
  adaptQuality(): void {
    const averageFPS = this.getAverageFPS();
    const targetFPS = this.config.targetFPS;

    // إذا كانت الأداء أقل من 80% من الهدف، قلل الجودة
    if (averageFPS < targetFPS * 0.8) {
      this.reduceQuality();
    }
    // إذا كانت الأداء أعلى من 95% من الهدف، زيادة الجودة
    else if (averageFPS > targetFPS * 0.95) {
      this.increaseQuality();
    }
  }

  /**
   * تقليل جودة المشهد
   */
  private reduceQuality(): void {
    if (this.config.enableShadows) {
      this.config.enableShadows = false;
      gameEvents.emit('quality_reduced', { feature: 'shadows' });
      console.log('⚠️ Shadows disabled for performance');
    } else if (this.config.shadowMapSize > 512) {
      this.config.shadowMapSize = Math.max(512, this.config.shadowMapSize / 2);
      gameEvents.emit('quality_reduced', { feature: 'shadow_resolution' });
      console.log(`⚠️ Shadow map size reduced to ${this.config.shadowMapSize}`);
    } else if (this.config.meshCullDistance > 100) {
      this.config.meshCullDistance = Math.max(100, this.config.meshCullDistance * 0.75);
      gameEvents.emit('quality_reduced', { feature: 'cull_distance' });
      console.log(`⚠️ Mesh cull distance reduced to ${this.config.meshCullDistance}`);
    }
  }

  /**
   * زيادة جودة المشهد
   */
  private increaseQuality(): void {
    if (!this.config.enableShadows) {
      this.config.enableShadows = true;
      gameEvents.emit('quality_increased', { feature: 'shadows' });
      console.log('✅ Shadows re-enabled');
    } else if (this.config.shadowMapSize < 2048) {
      this.config.shadowMapSize = Math.min(2048, this.config.shadowMapSize * 1.5);
      gameEvents.emit('quality_increased', { feature: 'shadow_resolution' });
      console.log(`✅ Shadow map size increased to ${this.config.shadowMapSize}`);
    } else if (this.config.meshCullDistance < 500) {
      this.config.meshCullDistance = Math.min(500, this.config.meshCullDistance * 1.25);
      gameEvents.emit('quality_increased', { feature: 'cull_distance' });
      console.log(`✅ Mesh cull distance increased to ${this.config.meshCullDistance}`);
    }
  }

  /**
   * تطبيق تحسينات الأداء
   */
  applyOptimizations(): void {
    // تحسين استدعاءات الرسم (Draw Calls)
    this.optimizeDrawCalls();

    // تحسين استخدام الذاكرة
    this.optimizeMemory();

    // تحسين المشاهد
    this.optimizeScenes();
  }

  /**
   * تحسين استدعاءات الرسم
   */
  private optimizeDrawCalls(): void {
    // يمكن دمج المشاهد والأشياء ذات الصلة
    // تطبيق instancing حيث أمكن
    // إزالة الأشياء غير المرئية

    if (this.metrics.drawCalls > this.config.maxDrawCalls) {
      gameEvents.emit('draw_calls_high', {
        current: this.metrics.drawCalls,
        max: this.config.maxDrawCalls,
      });
      console.warn(`⚠️ Draw calls (${this.metrics.drawCalls}) exceed limit`);
    }
  }

  /**
   * تحسين استخدام الذاكرة
   */
  private optimizeMemory(): void {
    if (typeof performance !== 'undefined' && (performance as any).memory) {
      const perfMemory = (performance as any).memory;
      const memUsage = perfMemory.usedJSHeapSize / 1048576; // Convert to MB
      this.metrics.memoryUsage = memUsage;

      const memLimit = perfMemory.jsHeapSizeLimit / 1048576;
      const percentUsage = (memUsage / memLimit) * 100;

      if (percentUsage > 85) {
        gameEvents.emit('memory_pressure', {
          usage: memUsage.toFixed(2),
          limit: memLimit.toFixed(2),
          percentage: percentUsage.toFixed(1),
        });
        console.warn(`⚠️ Memory usage high: ${percentUsage.toFixed(1)}%`);
      }
    }
  }

  /**
   * تحسين المشاهد
   */
  private optimizeScenes(): void {
    // تطبيق culling للكاميرا
    // تحسين النسج والمواد
    // تقليل دقة الظلال بناءً على المسافة
  }

  /**
   * طباعة تقرير الأداء
   */
  printPerformanceReport(): void {
    console.log(`
    ⚡ PERFORMANCE REPORT
    ─────────────────────
    FPS: ${this.metrics.fps.toFixed(1)} (Target: ${this.config.targetFPS})
    Average FPS: ${this.getAverageFPS().toFixed(1)}
    Frame Time: ${this.metrics.frameTime.toFixed(2)}ms

    Resources:
      Draw Calls: ${this.metrics.drawCalls}/${this.config.maxDrawCalls}
      Active Meshes: ${this.metrics.activeMeshes}
      Textures Loaded: ${this.metrics.texturesLoaded}
      Memory Usage: ${this.metrics.memoryUsage.toFixed(2)}MB

    Settings:
      LOD Enabled: ${this.config.enableLOD}
      Object Pooling: ${this.config.enableObjectPooling}
      Shadows: ${this.config.enableShadows}
      Shadow Map Size: ${this.config.shadowMapSize}
      Mesh Cull Distance: ${this.config.meshCullDistance}
    ─────────────────────
    `);
  }

  /**
   * تحديث إعدادات الأداء
   */
  setConfig(config: Partial<PerformanceConfig>): void {
    this.config = { ...this.config, ...config };
    gameEvents.emit('performance_config_changed', this.config);
  }

  /**
   * الحصول على الإعدادات الحالية
   */
  getConfig(): PerformanceConfig {
    return { ...this.config };
  }
}

// تصدير نسخة واحدة
export const performanceOptimizer = PerformanceOptimizer.getInstance();
