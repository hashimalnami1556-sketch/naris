/**
 * Minimap Component - الخريطة الصغيرة
 * يعرض خريطة صغيرة للمنطقة الحالية مع موقع اللاعب
 */

import React, { useEffect, useRef } from 'react';
import { gameEvents } from '../../game/core/EventSystem';

export interface MinimapProps {
  realm: string;
}

interface Position {
  x: number;
  y: number;
}

export const Minimap: React.FC<MinimapProps> = ({ realm }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const playerPosRef = useRef<Position>({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const CANVAS_SIZE = 200;
    const MAP_SIZE = 100; // units
    const SCALE = CANVAS_SIZE / MAP_SIZE;

    // Subscribe to position updates
    gameEvents.subscribe('character_moved', (data: any) => {
      playerPosRef.current = { x: data.position.x, y: data.position.z };
    });

    // Draw minimap
    const drawMinimap = () => {
      // Clear canvas
      ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
      ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // Draw grid
      ctx.strokeStyle = 'rgba(255, 169, 77, 0.1)';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 4; i++) {
        ctx.beginPath();
        ctx.moveTo((CANVAS_SIZE / 4) * i, 0);
        ctx.lineTo((CANVAS_SIZE / 4) * i, CANVAS_SIZE);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(0, (CANVAS_SIZE / 4) * i);
        ctx.lineTo(CANVAS_SIZE, (CANVAS_SIZE / 4) * i);
        ctx.stroke();
      }

      // Draw border
      ctx.strokeStyle = '#ffa94d';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // Draw player position
      const playerX = (playerPosRef.current.x + MAP_SIZE / 2) * SCALE;
      const playerY = (playerPosRef.current.y + MAP_SIZE / 2) * SCALE;

      // Player circle
      ctx.fillStyle = '#ff6b6b';
      ctx.beginPath();
      ctx.arc(playerX, playerY, 5, 0, Math.PI * 2);
      ctx.fill();

      // Player direction indicator
      ctx.strokeStyle = '#ff6b6b';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(playerX, playerY);
      ctx.lineTo(playerX, playerY - 10);
      ctx.stroke();

      requestAnimationFrame(drawMinimap);
    };

    drawMinimap();

    return () => {
      gameEvents.unsubscribe('character_moved');
    };
  }, []);

  return (
    <div className="minimap">
      <canvas ref={canvasRef} width={200} height={200} className="minimap-canvas" />
      <div
        style={{
          position: 'absolute',
          bottom: '5px',
          left: '5px',
          fontSize: '0.75rem',
          color: '#888',
          pointerEvents: 'none',
        }}
      >
        {realm.toUpperCase()}
      </div>
    </div>
  );
};
