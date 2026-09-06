/**
 * App Component - تطبيق اللعبة الرئيسي
 * يدير دورة حياة اللعبة والواجهة
 */

import React, { useEffect, useState } from 'react';
import { GameEngine } from './game/GameEngine';
import { gameEvents } from './game/core/EventSystem';
import { HUD } from './ui/hud/HUD';
import { LoadingScreen } from './ui/screens/LoadingScreen';
import { MainMenu } from './ui/screens/MainMenu';
import { PauseMenu } from './ui/screens/PauseMenu';
import { GameOverScreen } from './ui/screens/GameOverScreen';

export type GameScreenState = 'loading' | 'menu' | 'playing' | 'paused' | 'game_over';

export interface AppState {
  screenState: GameScreenState;
  initializationProgress: number;
  errorMessage: string;
}

export const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    screenState: 'loading',
    initializationProgress: 0,
    errorMessage: '',
  });

  useEffect(() => {
    const initializeGame = async () => {
      try {
        const engine = GameEngine.getInstance({
          canvasId: 'game-canvas',
          debug: true,
          autoStart: false,
        });

        // Subscribe to engine events
        gameEvents.subscribe('initialization_progress', (data: any) => {
          setAppState((prev) => ({
            ...prev,
            initializationProgress: data.progress,
          }));
        });

        gameEvents.subscribe('engine_initialized', () => {
          setAppState((prev) => ({
            ...prev,
            screenState: 'menu',
            initializationProgress: 100,
          }));
        });

        gameEvents.subscribe('engine_error', (data: any) => {
          setAppState((prev) => ({
            ...prev,
            screenState: 'loading',
            errorMessage: data.error,
          }));
          console.error('Engine error:', data.error);
        });

        gameEvents.subscribe('engine_started', () => {
          setAppState((prev) => ({
            ...prev,
            screenState: 'playing',
          }));
        });

        gameEvents.subscribe('engine_paused', () => {
          setAppState((prev) => ({
            ...prev,
            screenState: 'paused',
          }));
        });

        gameEvents.subscribe('engine_resumed', () => {
          setAppState((prev) => ({
            ...prev,
            screenState: 'playing',
          }));
        });

        // Initialize the engine
        await engine.initialize();
      } catch (error) {
        setAppState((prev) => ({
          ...prev,
          screenState: 'loading',
          errorMessage: String(error),
        }));
        console.error('Failed to initialize game:', error);
      }
    };

    initializeGame();

    // Cleanup
    return () => {
      // Unsubscribe all events when component unmounts
      gameEvents.clear();
    };
  }, []);

  const handleStartGame = () => {
    const engine = GameEngine.getInstance();
    engine.start();
  };

  const handleResumeGame = () => {
    const engine = GameEngine.getInstance();
    engine.resume();
  };

  const handlePauseGame = () => {
    const engine = GameEngine.getInstance();
    engine.pause();
  };

  const handleResetGame = () => {
    const engine = GameEngine.getInstance();
    engine.reset();
    setAppState((prev) => ({
      ...prev,
      screenState: 'menu',
    }));
  };

  return (
    <div className="game-container">
      {appState.screenState === 'loading' && (
        <LoadingScreen progress={appState.initializationProgress} error={appState.errorMessage} />
      )}

      {appState.screenState === 'menu' && <MainMenu onStartGame={handleStartGame} />}

      {appState.screenState === 'playing' && <HUD onPauseGame={handlePauseGame} />}

      {appState.screenState === 'paused' && (
        <PauseMenu onResumeGame={handleResumeGame} onResetGame={handleResetGame} />
      )}

      {appState.screenState === 'game_over' && (
        <GameOverScreen onResetGame={handleResetGame} />
      )}
    </div>
  );
};
