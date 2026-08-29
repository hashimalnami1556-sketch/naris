import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const cards = [
  ['Assets', '0', 'Canonical manifest'],
  ['Validated', '0%', 'CI quality gate'],
  ['Builds', '0', 'Release candidates'],
  ['Blocked', '0', 'Needs attention'],
];

function App() {
  return <main className="shell">
    <aside><div className="brand">NARIS<span> / v2.0</span></div><nav>{['Overview','Assets','Characters','Environments','Weapons','VFX','Scenes','CI / Builds','QA','Releases'].map((x,i)=><div className={i===0?'active':''} key={x}>{x}</div>)}</nav></aside>
    <section className="content"><header><div><p className="eyebrow">MASTER PRODUCTION CONTROL PLANE</p><h1>Production Cockpit</h1><p className="muted">GitHub → CI → Linear → Playable Master</p></div><div className="status"><i/> Pipeline operational</div></header>
      <section className="grid">{cards.map(c=><article key={c[0]}><p>{c[0]}</p><strong>{c[1]}</strong><small>{c[2]}</small></article>)}</section>
      <section className="panel"><div className="panelHead"><h2>Release Gates</h2><span>v2.0 foundation</span></div>{['Manifest integrity','Schema validation','Dependency validation','Automated smoke tests','Build / export','Playtest acceptance'].map(x=><div className="gate" key={x}><b>{x}</b><span>Pending</span></div>)}</section>
    </section>
  </main>
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
