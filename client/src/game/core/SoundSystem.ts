/**
 * Sound System - نظام الصوت
 * إدارة الموسيقى والمؤثرات الصوتية
 */

import { gameEvents } from './EventSystem';

export type SoundType = 'music' | 'sfx' | 'voice' | 'ambient';

export interface SoundConfig {
  url: string;
  type: SoundType;
  volume?: number;
  loop?: boolean;
  autoPlay?: boolean;
}

export class SoundSystem {
  private static instance: SoundSystem;
  private audioContext: AudioContext | null = null;
  private audioBuffers: Map<string, AudioBuffer> = new Map();
  private audioSources: Map<string, AudioBufferSource> = new Map();
  private masterVolume: number = 1;
  private typeVolumes: Record<SoundType, number> = {
    music: 0.7,
    sfx: 0.8,
    voice: 1.0,
    ambient: 0.5,
  };
  private isEnabled: boolean = true;

  private constructor() {
    this.initializeAudioContext();
    console.log('🔊 SoundSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الصوت
   */
  static getInstance(): SoundSystem {
    if (!SoundSystem.instance) {
      SoundSystem.instance = new SoundSystem();
    }
    return SoundSystem.instance;
  }

  /**
   * تهيئة سياق الصوت
   */
  private initializeAudioContext(): void {
    if (typeof window !== 'undefined' && !this.audioContext) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        this.audioContext = new AudioContextClass();
        console.log('✓ Web Audio API initialized');
      }
    }
  }

  /**
   * تحميل ملف صوتي
   */
  async loadSound(soundId: string, config: SoundConfig): Promise<boolean> {
    if (!this.audioContext) {
      console.warn('AudioContext not available');
      return false;
    }

    if (this.audioBuffers.has(soundId)) {
      return true;
    }

    try {
      const response = await fetch(config.url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.audioBuffers.set(soundId, audioBuffer);

      gameEvents.emit('sound_loaded', { soundId, type: config.type });
      console.log(`✓ Sound loaded: ${soundId}`);

      if (config.autoPlay) {
        this.playSound(soundId, config.type, config.volume);
      }

      return true;
    } catch (error) {
      console.error(`Failed to load sound ${soundId}:`, error);
      return false;
    }
  }

  /**
   * تشغيل صوت
   */
  playSound(soundId: string, type: SoundType = 'sfx', volume?: number): void {
    if (!this.audioContext || !this.isEnabled) return;

    const audioBuffer = this.audioBuffers.get(soundId);
    if (!audioBuffer) {
      console.warn(`Sound not found: ${soundId}`);
      return;
    }

    // Stop existing source if any
    this.stopSound(soundId);

    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;

    // Create gain node for volume control
    const gainNode = this.audioContext.createGain();
    const finalVolume = (volume || this.typeVolumes[type]) * this.masterVolume;
    gainNode.gain.setValueAtTime(finalVolume, this.audioContext.currentTime);

    source.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    source.onended = () => {
      this.audioSources.delete(soundId);
      gameEvents.emit('sound_ended', { soundId });
    };

    source.start(0);
    this.audioSources.set(soundId, source);

    gameEvents.emit('sound_started', { soundId, type });
  }

  /**
   * إيقاف صوت
   */
  stopSound(soundId: string): void {
    const source = this.audioSources.get(soundId);
    if (source) {
      try {
        source.stop();
      } catch (e) {
        // Already stopped
      }
      this.audioSources.delete(soundId);
      gameEvents.emit('sound_stopped', { soundId });
    }
  }

  /**
   * إيقاف جميع الأصوات
   */
  stopAllSounds(): void {
    this.audioSources.forEach((source, soundId) => {
      this.stopSound(soundId);
    });
  }

  /**
   * تعيين مستوى الصوت الرئيسي
   */
  setMasterVolume(volume: number): void {
    this.masterVolume = Math.max(0, Math.min(1, volume));
    gameEvents.emit('master_volume_changed', { volume: this.masterVolume });
  }

  /**
   * تعيين مستوى الصوت لنوع معين
   */
  setTypeVolume(type: SoundType, volume: number): void {
    this.typeVolumes[type] = Math.max(0, Math.min(1, volume));
    gameEvents.emit('type_volume_changed', { type, volume });
  }

  /**
   * تفعيل/تعطيل الصوت
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    if (!enabled) {
      this.stopAllSounds();
    }
    gameEvents.emit('audio_enabled_changed', { enabled });
  }

  /**
   * الحصول على إحصائيات الصوت
   */
  getStats(): { buffersLoaded: number; soundsPlaying: number; masterVolume: number } {
    return {
      buffersLoaded: this.audioBuffers.size,
      soundsPlaying: this.audioSources.size,
      masterVolume: this.masterVolume,
    };
  }

  /**
   * تنظيف جميع الموارد الصوتية
   */
  dispose(): void {
    this.stopAllSounds();
    this.audioBuffers.clear();
    this.audioSources.clear();
    if (this.audioContext) {
      this.audioContext.close().catch(() => {
        // Already closed
      });
    }
    console.log('🗑️ SoundSystem disposed');
  }
}

// تصدير نسخة واحدة
export const soundSystem = SoundSystem.getInstance();
