import test from 'node:test';
import assert from 'node:assert/strict';
import { productionState, deriveSummary } from './productionState.mjs';

test('shipping readiness is blocked when runtime evidence is missing', () => {
  const summary = deriveSummary(productionState);
  assert.equal(summary.shipping.status, 'blocked');
  assert.match(summary.shipping.reason, /Windows Unreal/i);
});

test('overview never reports pipeline operational without runtime evidence', () => {
  const summary = deriveSummary(productionState);
  assert.notEqual(summary.pipelineLabel, 'Pipeline operational');
});

test('W04 progression preserves the canonical playable order', () => {
  assert.deepEqual(
    productionState.w04.map(step => step.name),
    ['Main Menu','Intro','Wake Area','Movement / Combat','Memory Crystal','First Whisper','Ash Gate','Celestial Wolf','Bone Beast','Demo End']
  );
});

test('critical blockers are exposed as first-class summary data', () => {
  const summary = deriveSummary(productionState);
  assert.ok(summary.blockers.length >= 4);
  assert.ok(summary.blockers.some(item => /production map/i.test(item)));
});
