import React from 'react';
import { createRoot } from 'react-dom/client';
import { productionState, deriveSummary } from './productionState.mjs';
import './styles.css';

const nav = ['Overview','Assets','Characters','Environments','Weapons','VFX / Audio','Scenes / Worlds','CI / Builds','QA / Playtests','Releases'];
const summary = deriveSummary(productionState);
const tone = (status: string) => `pill ${status}`;

function App() {
  return <main className="shell">
    <aside>
      <div className="brand">NARIS<span> / CONTROL</span></div>
      <p className="sideLabel">W04 · ASHEN FOREST</p>
      <nav>{nav.map((item,i)=><button className={i===0?'active':''} key={item}>{item}</button>)}</nav>
      <div className="source"><span>Source of truth</span><b>GitHub / main</b><small>State snapshot: {productionState.updatedAt}</small></div>
    </aside>

    <section className="content">
      <header>
        <div><p className="eyebrow">MASTER PRODUCTION CONTROL PLANE</p><h1>W04 Production Readiness</h1><p className="muted">Evidence first · no inferred runtime readiness</p></div>
        <div className="runtime"><span className="dot pending"/><div><b>{summary.pipelineLabel}</b><small>Windows Unreal evidence required</small></div></div>
      </header>

      <section className="hero">
        <div><p className="eyebrow">SHIPPING RC</p><h2>Blocked by production evidence</h2><p>{summary.shipping.reason}.</p></div>
        <div className="heroStat"><strong>{summary.blockers.length}</strong><span>active blockers</span></div>
      </section>

      <section className="metrics">
        <article><span>Gate passes</span><strong>{summary.gatePasses}<i> / {summary.gateTotal}</i></strong><small>Strict evidence model</small></article>
        <article><span>Static CI</span><strong className="okText">Passed</strong><small>Not runtime proof</small></article>
        <article><span>Windows Unreal</span><strong className="warnText">Missing</strong><small>Build · package · playtest</small></article>
        <article><span>Production map</span><strong className="warnText">Unverified</strong><small>W04_AshenForest</small></article>
      </section>

      <section className="twoCol">
        <section className="panel">
          <div className="panelHead"><div><p className="eyebrow">PLAYABLE LOOP</p><h2>W04 progression</h2></div><span>Implementation ≠ runtime proof</span></div>
          <div className="progression">{productionState.w04.map((step,index)=><div className="step" key={step.name}><span className="stepIndex">{String(index+1).padStart(2,'0')}</span><div><b>{step.name}</b><small>Source implementation present</small></div><span className={tone(step.status)}>{step.status}</span></div>)}</div>
        </section>

        <section className="panel blockers">
          <div className="panelHead"><div><p className="eyebrow dangerText">RELEASE IMPACT</p><h2>Critical blockers</h2></div><span>{summary.blockers.length} open</span></div>
          {summary.blockers.map((item,index)=><div className="blocker" key={item}><span>{index+1}</span><p>{item}</p></div>)}
        </section>
      </section>

      <section className="panel gates">
        <div className="panelHead"><div><p className="eyebrow">EVIDENCE MATRIX</p><h2>Release gates</h2></div><span>Canonical snapshot</span></div>
        <div className="gateHeader"><span>Gate</span><span>Evidence</span><span>Status</span></div>
        {productionState.gates.map(g=><div className="gate" key={g.name}><b>{g.name}</b><p>{g.evidence}</p><span className={tone(g.status)}>{g.status}</span></div>)}
      </section>

      <footer><span>Next action</span><b>Bring the Windows self-hosted Unreal environment online and produce verifiable build/package/playtest evidence.</b></footer>
    </section>
  </main>
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
