/**
 * Audio System - نظام الصوت والموسيقى
 * إدارة المؤثرات الصوتية والموسيقى التكيفية والصوت المكاني
 */

import { gameEvents } from './EventSystem';

export interface AudioClip {
  id: string;
  url: string;
  duration: number;
  isLoaded: boolean;
}

export interface SoundEffect {
  id: string;
  name: string;
  volume: number;
  pitch: number;
  isPlaying: boolean;
  loop: boolean;
}

export interface MusicTrack {
  id: string;
  name: string;
  intensity: 'calm' | 'exploration' | 'combat' | 'boss' | 'victory' | 'defeat';
  volume: number;
  isPlaying: boolean;
  transitionDuration: number;
}

export interface AudioConfig {
  masterVolume: number;
  sfxVolume: number;
  musicVolume: number;
  ambienceVolume: number;
  maxSimultaneousSounds: number;
  usesSpatialAudio: boolean;
}

export class AudioSystem {
  private static instance: AudioSystem;
  private audioContext: AudioContext | null = null;
  private audioClips: Map<string, AudioClip> = new Map();
  private activeSoundEffects: Map<string, SoundEffect> = new Map();
  private currentMusicTrack: MusicTrack | null = null;
  private config: AudioConfig = {
    masterVolume: 1.0,
    sfxVolume: 0.8,
    musicVolume: 0.6,
    ambienceVolume: 0.5,
    maxSimultaneousSounds: 32,
    usesSpatialAudio: true,
  };
  private musicTransitionTimeout: NodeJS.Timeout | null = null;
  private spatialAudioEnabled: boolean = false;

  private constructor() {
    console.log('🔊 AudioSystem initialized');
    this.initializeAudioContext();
    this.setupEventSubscriptions();
  }

  /**
   * الحصول على نسخة واحدة من نظام الصوت
   */
  static getInstance(): AudioSystem {
    if (!AudioSystem.instance) {
      AudioSystem.instance = new AudioSystem();
    }
    return AudioSystem.instance;
  }

  /**
   * تهيئة Audio Context
   */
  private initializeAudioContext(): void {
    try {
      const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
      this.audioContext = new AudioContextClass();

      // Resume audio context on user interaction
      const resumeAudio = () => {
        if (this.audioContext && this.audioContext.state === 'suspended') {
          this.audioContext.resume().then(() => {
            console.log('✓ AudioContext resumed');
            document.removeEventListener('click', resumeAudio);
            document.removeEventListener('touchstart', resumeAudio);
          });
        }
      };

      document.addEventListener('click', resumeAudio);
      document.addEventListener('touchstart', resumeAudio);

      console.log('✓ AudioContext initialized');
    } catch (error) {
      console.warn('⚠️ AudioContext not available:', error);
    }
  }

  /**
   * إعداد اشتراكات الأحداث الصوتية
   */
  private setupEventSubscriptions(): void {
    // Combat sounds
    gameEvents.subscribe('attack_executed', (data: any) => {
      this.playSoundEffect('attack_' + data.damageType, 0.7);
      if (data.hasWeakness > 1) {
        this.playSoundEffect('critical_hit', 0.9);
      }
    });

    // Hit-Stop feedback
    gameEvents.subscribe('hit_stop', () => {
      this.playSoundEffect('hit_impact', 0.8);
    });

    // Ability usage
    gameEvents.subscribe('ability_used', () => {
      this.playSoundEffect('ability_cast', 0.8);
    });

    // Enemy defeated
    gameEvents.subscribe('enemy_defeated', () => {
      this.switchMusicTrack('victory', 1.5);
      this.playSoundEffect('enemy_defeated', 0.9);
    });

    // Realm switches
    gameEvents.subscribe('realm_switched', () => {
      this.switchMusicTrack('exploration', 2.0);
      this.playSoundEffect('realm_transition', 0.7);
    });

    // Status effects
    gameEvents.subscribe('status_effect_applied', (data: any) => {
      this.playSoundEffect('status_' + data.effect, 0.6);
    });

    // Boss encounter starts
    gameEvents.subscribe('boss_encounter_start', () => {
      this.switchMusicTrack('boss', 2.5);
      this.playSoundEffect('boss_appear', 1.0);
    });

    // Victory/Defeat
    gameEvents.subscribe('combat_victory', () => {
      this.switchMusicTrack('victory', 2.0);
      this.playSoundEffect('victory_fanfare', 1.0);
    });

    gameEvents.subscribe('player_defeated', () => {
      this.switchMusicTrack('defeat', 2.0);
      this.playSoundEffect('defeat_sound', 0.9);
    });

    // UI interactions
    gameEvents.subscribe('ui_click', () => {
      this.playSoundEffect('ui_click', 0.5);
    });

    gameEvents.subscribe('ui_hover', () => {
      this.playSoundEffect('ui_hover', 0.3);
    });
  }

  /**
   * تحميل مقطع صوتي
   */
  loadAudioClip(id: string, url: string): Promise<AudioClip> {
    return new Promise((resolve, reject) => {
      if (this.audioClips.has(id)) {
        resolve(this.audioClips.get(id)!);
        return;
      }

      fetch(url)
        .then((response) => response.arrayBuffer())
        .then((arrayBuffer) => {
          if (!this.audioContext) {
            reject(new Error('AudioContext not initialized'));
            return;
          }

          this.audioContext.decodeAudioData(
            arrayBuffer,
            (audioBuffer) => {
              const clip: AudioClip = {
                id,
                url,
                duration: audioBuffer.duration,
                isLoaded: true,
              };
              this.audioClips.set(id, clip);
              console.log(`✓ Audio clip loaded: ${id} (${audioBuffer.duration.toFixed(2)}s)`);
              resolve(clip);
            },
            (error) => {
              console.error('✗ Failed to decode audio:', error);
              reject(error);
            }
          );
        })
        .catch((error) => {
          console.error('✗ Failed to load audio:', error);
          reject(error);
        });
    });
  }

  /**
   * تشغيل مؤثر صوتي
   */
  playSoundEffect(effectName: string, volume: number = 1.0): string {
    if (!this.audioContext) {
      console.warn('⚠️ AudioContext not available');
      return '';
    }

    // Check simultaneous sound limit
    if (this.activeSoundEffects.size >= this.config.maxSimultaneousSounds) {
      console.warn(
        `⚠️ Max simultaneous sounds reached (${this.config.maxSimultaneousSounds})`
      );
      return '';
    }

    const soundId = `sfx_${effectName}_${Date.now()}`;
    const adjustedVolume = volume * this.config.sfxVolume * this.config.masterVolume;

    const sound: SoundEffect = {
      id: soundId,
      name: effectName,
      volume: adjustedVolume,
      pitch: 1.0,
      isPlaying: true,
      loop: false,
    };

    this.activeSoundEffects.set(soundId, sound);

    // Simulate sound playback
    setTimeout(() => {
      this.activeSoundEffects.delete(soundId);
      sound.isPlaying = false;
    }, 500); // Default SFX duration

    gameEvents.emit('sound_effect_played', {
      effectName,
      soundId,
      volume: adjustedVolume,
    });

    console.log(`🔊 SFX played: ${effectName} (ID: ${soundId})`);
    return soundId;
  }

  /**
   * تبديل المسار الموسيقي
   */
  switchMusicTrack(
    intensity: MusicTrack['intensity'],
    transitionDuration: number = 2.0
  ): void {
    // Create new music track
    const newTrack: MusicTrack = {
      id: `music_${intensity}_${Date.now()}`,
      name: `Music - ${intensity}`,
      intensity,
      volume: this.config.musicVolume * this.config.masterVolume,
      isPlaying: true,
      transitionDuration,
    };

    // Handle fade out of current track
    if (this.musicTransitionTimeout) {
      clearTimeout(this.musicTransitionTimeout);
    }

    if (this.currentMusicTrack) {
      gameEvents.emit('music_transition_start', {
        fromIntensity: this.currentMusicTrack.intensity,
        toIntensity: intensity,
        duration: transitionDuration,
      });
    }

    // Schedule track change
    this.musicTransitionTimeout = setTimeout(() => {
      this.currentMusicTrack = newTrack;
      gameEvents.emit('music_track_changed', {
        trackId: newTrack.id,
        intensity,
        volume: newTrack.volume,
      });
      console.log(`🎵 Music changed to: ${intensity}`);
    }, transitionDuration * 1000);
  }

  /**
   * تشغيل الموسيقى
   */
  playMusic(): void {
    if (this.currentMusicTrack) {
      this.currentMusicTrack.isPlaying = true;
      gameEvents.emit('music_resumed', {
        trackId: this.currentMusicTrack.id,
      });
      console.log('🎵 Music resumed');
    }
  }

  /**
   * إيقاف الموسيقى
   */
  pauseMusic(): void {
    if (this.currentMusicTrack) {
      this.currentMusicTrack.isPlaying = false;
      gameEvents.emit('music_paused', {
        trackId: this.currentMusicTrack.id,
      });
      console.log('⏸️ Music paused');
    }
  }

  /**
   * تشغيل صوت محيط (Ambience)
   */
  playAmbience(ambienceName: string, volume: number = 1.0): string {
    const adjustedVolume = volume * this.config.ambienceVolume * this.config.masterVolume;
    const ambienceId = `ambience_${ambienceName}_${Date.now()}`;

    gameEvents.emit('ambience_started', {
      ambienceName,
      ambienceId,
      volume: adjustedVolume,
    });

    console.log(`🌍 Ambience started: ${ambienceName}`);
    return ambienceId;
  }

  /**
   * إيقاف صوت محيط
   */
  stopAmbience(ambienceId: string): void {
    gameEvents.emit('ambience_stopped', {
      ambienceId,
    });
    console.log(`🌍 Ambience stopped: ${ambienceId}`);
  }

  /**
   * تعيين مستوى الصوت الرئيسي
   */
  setMasterVolume(volume: number): void {
    this.config.masterVolume = Math.max(0, Math.min(1, volume));
    gameEvents.emit('master_volume_changed', {
      volume: this.config.masterVolume,
    });
    console.log(`🔊 Master volume: ${(this.config.masterVolume * 100).toFixed(0)}%`);
  }

  /**
   * تعيين مستوى صوت المؤثرات الصوتية
   */
  setSFXVolume(volume: number): void {
    this.config.sfxVolume = Math.max(0, Math.min(1, volume));
    gameEvents.emit('sfx_volume_changed', {
      volume: this.config.sfxVolume,
    });
  }

  /**
   * تعيين مستوى صوت الموسيقى
   */
  setMusicVolume(volume: number): void {
    this.config.musicVolume = Math.max(0, Math.min(1, volume));
    if (this.currentMusicTrack) {
      this.currentMusicTrack.volume = this.config.musicVolume * this.config.masterVolume;
    }
    gameEvents.emit('music_volume_changed', {
      volume: this.config.musicVolume,
    });
  }

  /**
   * تعيين مستوى صوت المحيط
   */
  setAmbienceVolume(volume: number): void {
    this.config.ambienceVolume = Math.max(0, Math.min(1, volume));
    gameEvents.emit('ambience_volume_changed', {
      volume: this.config.ambienceVolume,
    });
  }

  /**
   * إيقاف جميع المؤثرات الصوتية
   */
  stopAllSoundEffects(): void {
    this.activeSoundEffects.forEach((sound) => {
      sound.isPlaying = false;
    });
    this.activeSoundEffects.clear();
    console.log('🔇 All sound effects stopped');
  }

  /**
   * الحصول على إعدادات الصوت
   */
  getAudioConfig(): Readonly<AudioConfig> {
    return { ...this.config };
  }

  /**
   * تحديث إعدادات الصوت
   */
  setAudioConfig(config: Partial<AudioConfig>): void {
    this.config = { ...this.config, ...config };
    gameEvents.emit('audio_config_changed', this.config);
    console.log('✓ Audio config updated');
  }

  /**
   * تفعيل/تعطيل الصوت المكاني
   */
  setSpatialAudioEnabled(enabled: boolean): void {
    this.spatialAudioEnabled = enabled;
    this.config.usesSpatialAudio = enabled;
    gameEvents.emit('spatial_audio_toggled', {
      enabled,
    });
    console.log(`${enabled ? '✓' : '✗'} Spatial audio ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * حساب صوت المسافة (Distance Attenuation)
   */
  calculateDistanceAttenuation(distance: number, maxDistance: number = 100): number {
    if (distance >= maxDistance) return 0;
    return Math.max(0, 1 - distance / maxDistance);
  }

  /**
   * حساب زاوية التوزيع الستيريو (Panning)
   */
  calculateStereoBalance(angleRadians: number): number {
    return Math.sin(angleRadians);
  }

  /**
   * الحصول على معلومات الموسيقى الحالية
   */
  getCurrentMusicTrack(): MusicTrack | null {
    return this.currentMusicTrack ? { ...this.currentMusicTrack } : null;
  }

  /**
   * طباعة معلومات نظام الصوت
   */
  printAudioInfo(): void {
    console.log(`
    🔊 AUDIO SYSTEM STATUS
    ─────────────────────
    AudioContext State: ${this.audioContext?.state || 'Not initialized'}
    Master Volume: ${(this.config.masterVolume * 100).toFixed(0)}%
    SFX Volume: ${(this.config.sfxVolume * 100).toFixed(0)}%
    Music Volume: ${(this.config.musicVolume * 100).toFixed(0)}%
    Ambience Volume: ${(this.config.ambienceVolume * 100).toFixed(0)}%

    Current Music: ${this.currentMusicTrack?.intensity || 'None'}
    Active Sound Effects: ${this.activeSoundEffects.size}/${this.config.maxSimultaneousSounds}
    Loaded Clips: ${this.audioClips.size}
    Spatial Audio: ${this.spatialAudioEnabled ? '✓' : '✗'}
    ─────────────────────
    `);
  }

  /**
   * تنظيف نظام الصوت
   */
  cleanup(): void {
    this.stopAllSoundEffects();
    this.pauseMusic();
    if (this.musicTransitionTimeout) {
      clearTimeout(this.musicTransitionTimeout);
    }
    this.audioClips.clear();
    this.activeSoundEffects.clear();
    if (this.audioContext) {
      this.audioContext.close().catch((e) =>
        console.warn('⚠️ Error closing AudioContext:', e)
      );
    }
    console.log('✓ Audio System cleaned up');
  }
}

// تصدير نسخة واحدة
export const audioSystem = AudioSystem.getInstance();
