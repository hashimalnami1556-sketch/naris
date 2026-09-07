import { useEffect, useRef, useState } from 'react';
import { GameRoot } from './game/core/GameRoot';
import type { CharacterId } from './game/core/GameState';
import './styles.css';

const chars: { id: CharacterId; label: string; key: string }[] = [
  { id: 'ash', label: 'آش', key: '1' }, { id: 'rune', label: 'رون', key: '2' }, { id: 'kor', label: 'كور', key: '3' }
];

export default function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<GameRoot | null>(null);
  const [character, setCharacter] = useState<CharacterId>('ash');
  const [health, setHealth] = useState(100);
  const [shards, setShards] = useState(0);
  const [status, setStatus] = useState('استيقاظ الرماد');

  useEffect(() => {
    if (!canvasRef.current) return;
    const game = new GameRoot(canvasRef.current); gameRef.current = game;
    const offCharacter = game.bus.on('character.changed', ({ id }) => setCharacter(id as CharacterId));
    const offDamage = game.bus.on('player.damaged', ({ health: h }) => setHealth(h));
    const offKill = game.bus.on('combat.enemyDefeated', ({ xp }) => setStatus(`سقط العدو · +${xp} خبرة الرماد`));
    return () => { offCharacter(); offDamage(); offKill(); game.dispose(); gameRef.current = null; };
  }, []);

  const switchCharacter = (id: CharacterId) => gameRef.current?.player.switchTo(id);
  return <main className="naris-shell">
    <canvas ref={canvasRef} className="naris-canvas" />
    <div className="vignette" />
    <header className="hud-top">
      <div className="realm-title"><span>W04</span><strong>غابة الرماد</strong><small>{status}</small></div>
      <div className="health"><div className="health-label"><span>الحياة</span><b>{Math.round(health)}</b></div><div className="health-track"><i style={{ width: `${health}%` }} /></div></div>
      <div className="shards"><span>شظايا الرماد</span><b>{shards}</b></div>
    </header>
    <aside className="character-wheel" aria-label="تبديل الشخصية">
      {chars.map((c) => <button key={c.id} className={character === c.id ? 'active' : ''} onClick={() => switchCharacter(c.id)}><span>{c.key}</span>{c.label}</button>)}
    </aside>
    <div className="objective"><span>الهدف الحالي</span><strong>اجمع 5 شظايا الرماد</strong><small>استكشف الطريق نحو البوابة القديمة</small></div>
    <div className="controls"><kbd>W A S D</kbd><span>الحركة</span><kbd>SPACE</kbd><span>هجوم</span><span>1 / 2 / 3 تبديل</span></div>
  </main>;
}
