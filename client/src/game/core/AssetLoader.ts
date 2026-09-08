/**
 * Asset Loader - نظام تحميل الأصول
 * تحميل وتخزين مؤقت لجميع أصول اللعبة (نماذج، نسيج، صوت، إلخ)
 */

import { LoadCallback } from '../../types/gameTypes';

interface LoadedAsset {
  name: string;
  data: any;
  type: string;
  timestamp: number;
}

export class AssetLoader {
  private static instance: AssetLoader;
  private cache: Map<string, LoadedAsset> = new Map();
  private loading: Map<string, Promise<any>> = new Map();
  private loadCallbacks: LoadCallback[] = [];
  private totalAssets: number = 0;
  private loadedAssets: number = 0;

  private constructor() {
    console.log('📦 AssetLoader initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام تحميل الأصول
   */
  static getInstance(): AssetLoader {
    if (!AssetLoader.instance) {
      AssetLoader.instance = new AssetLoader();
    }
    return AssetLoader.instance;
  }

  /**
   * تسجيل استدعاء تقدم التحميل
   */
  onProgress(callback: LoadCallback): void {
    this.loadCallbacks.push(callback);
  }

  /**
   * إزالة استدعاء تقدم التحميل
   */
  offProgress(callback: LoadCallback): void {
    const index = this.loadCallbacks.indexOf(callback);
    if (index > -1) {
      this.loadCallbacks.splice(index, 1);
    }
  }

  /**
   * بث تحديث التقدم
   */
  private reportProgress(): void {
    const progress = this.totalAssets > 0 ? this.loadedAssets / this.totalAssets : 0;
    this.loadCallbacks.forEach((callback) => callback(progress));
  }

  /**
   * تحميل ملف JSON (بيانات)
   */
  async loadJSON<T>(url: string, name: string = url): Promise<T> {
    // فحص الذاكرة المؤقتة
    if (this.cache.has(name)) {
      console.log(`📦 Asset from cache: ${name}`);
      return this.cache.get(name)!.data as T;
    }

    // فحص إذا كان التحميل جارياً
    if (this.loading.has(name)) {
      return this.loading.get(name)!;
    }

    // بدء التحميل
    const promise = fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error(`Failed to load ${name}: ${response.statusText}`);
        return response.json();
      })
      .then((data) => {
        this.cache.set(name, {
          name,
          data,
          type: 'json',
          timestamp: Date.now(),
        });
        this.loadedAssets++;
        this.reportProgress();
        console.log(`✓ Loaded JSON: ${name}`);
        return data as T;
      })
      .catch((error) => {
        console.error(`✗ Failed to load JSON: ${name}`, error);
        throw error;
      });

    this.loading.set(name, promise);
    this.totalAssets++;

    try {
      return await promise;
    } finally {
      this.loading.delete(name);
    }
  }

  /**
   * تحميل نسيج (Texture)
   */
  async loadTexture(url: string, name: string = url): Promise<ImageBitmap> {
    if (this.cache.has(name)) {
      console.log(`📦 Texture from cache: ${name}`);
      return this.cache.get(name)!.data as ImageBitmap;
    }

    if (this.loading.has(name)) {
      return this.loading.get(name)!;
    }

    const promise = fetch(url)
      .then((response) => response.blob())
      .then((blob) => createImageBitmap(blob))
      .then((bitmap) => {
        this.cache.set(name, {
          name,
          data: bitmap,
          type: 'texture',
          timestamp: Date.now(),
        });
        this.loadedAssets++;
        this.reportProgress();
        console.log(`✓ Loaded Texture: ${name}`);
        return bitmap;
      })
      .catch((error) => {
        console.error(`✗ Failed to load texture: ${name}`, error);
        throw error;
      });

    this.loading.set(name, promise);
    this.totalAssets++;

    try {
      return await promise;
    } finally {
      this.loading.delete(name);
    }
  }

  /**
   * تحميل صوت
   */
  async loadAudio(url: string, name: string = url): Promise<ArrayBuffer> {
    if (this.cache.has(name)) {
      console.log(`📦 Audio from cache: ${name}`);
      return this.cache.get(name)!.data as ArrayBuffer;
    }

    if (this.loading.has(name)) {
      return this.loading.get(name)!;
    }

    const promise = fetch(url)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        this.cache.set(name, {
          name,
          data: buffer,
          type: 'audio',
          timestamp: Date.now(),
        });
        this.loadedAssets++;
        this.reportProgress();
        console.log(`✓ Loaded Audio: ${name}`);
        return buffer;
      })
      .catch((error) => {
        console.error(`✗ Failed to load audio: ${name}`, error);
        throw error;
      });

    this.loading.set(name, promise);
    this.totalAssets++;

    try {
      return await promise;
    } finally {
      this.loading.delete(name);
    }
  }

  /**
   * تحميل ملف GLB/GLTF (نموذج ثلاثي الأبعاد)
   */
  async loadModel(url: string, name: string = url): Promise<ArrayBuffer> {
    if (this.cache.has(name)) {
      console.log(`📦 Model from cache: ${name}`);
      return this.cache.get(name)!.data as ArrayBuffer;
    }

    if (this.loading.has(name)) {
      return this.loading.get(name)!;
    }

    const promise = fetch(url)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        this.cache.set(name, {
          name,
          data: buffer,
          type: 'model',
          timestamp: Date.now(),
        });
        this.loadedAssets++;
        this.reportProgress();
        console.log(`✓ Loaded Model: ${name}`);
        return buffer;
      })
      .catch((error) => {
        console.error(`✗ Failed to load model: ${name}`, error);
        throw error;
      });

    this.loading.set(name, promise);
    this.totalAssets++;

    try {
      return await promise;
    } finally {
      this.loading.delete(name);
    }
  }

  /**
   * تحميل عدة أصول بالتوازي
   */
  async loadMultiple(
    assets: Array<{ url: string; name: string; type: 'json' | 'texture' | 'audio' | 'model' }>
  ): Promise<Map<string, any>> {
    const results = new Map<string, any>();

    const promises = assets.map(async (asset) => {
      try {
        let data: any;
        switch (asset.type) {
          case 'json':
            data = await this.loadJSON(asset.url, asset.name);
            break;
          case 'texture':
            data = await this.loadTexture(asset.url, asset.name);
            break;
          case 'audio':
            data = await this.loadAudio(asset.url, asset.name);
            break;
          case 'model':
            data = await this.loadModel(asset.url, asset.name);
            break;
        }
        results.set(asset.name, data);
      } catch (error) {
        console.error(`Failed to load asset: ${asset.name}`, error);
      }
    });

    await Promise.all(promises);
    return results;
  }

  /**
   * الحصول على أصل من الذاكرة المؤقتة
   */
  get<T>(name: string): T | null {
    const asset = this.cache.get(name);
    return asset ? (asset.data as T) : null;
  }

  /**
   * فحص وجود أصل
   */
  has(name: string): boolean {
    return this.cache.has(name);
  }

  /**
   * حذف أصل من الذاكرة المؤقتة
   */
  unload(name: string): void {
    this.cache.delete(name);
    console.log(`🗑️ Unloaded asset: ${name}`);
  }

  /**
   * تفريغ جميع الأصول
   */
  unloadAll(): void {
    this.cache.clear();
    this.loading.clear();
    this.loadedAssets = 0;
    this.totalAssets = 0;
    console.log('🗑️ All assets unloaded');
  }

  /**
   * الحصول على إحصائيات الذاكرة المؤقتة
   */
  getStats(): {
    cached: number;
    loading: number;
    totalLoaded: number;
    progress: number;
  } {
    return {
      cached: this.cache.size,
      loading: this.loading.size,
      totalLoaded: this.loadedAssets,
      progress: this.totalAssets > 0 ? this.loadedAssets / this.totalAssets : 0,
    };
  }

  /**
   * طباعة إحصائيات الأصول
   */
  printStats(): void {
    const stats = this.getStats();
    console.log(`
    📊 Asset Loader Statistics
    ─────────────────────────
    Cached Assets: ${stats.cached}
    Loading: ${stats.loading}
    Total Loaded: ${stats.totalLoaded}
    Progress: ${(stats.progress * 100).toFixed(1)}%
    ─────────────────────────
    `);
  }

  /**
   * قائمة جميع الأصول المخزنة مؤقتًا
   */
  listCached(): void {
    console.log('📦 Cached Assets:');
    this.cache.forEach((asset, name) => {
      console.log(`  ${name} (${asset.type})`);
    });
  }
}

// تصدير نسخة واحدة
export const assetLoader = AssetLoader.getInstance();
