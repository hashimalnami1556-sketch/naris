export const productionState = {
  updatedAt: '2026-09-23',
  evidence: {
    staticCI: { status: 'passed', label: 'Static CI', detail: 'Repository validation evidence exists.' },
    windowsUnreal: { status: 'missing', label: 'Windows Unreal', detail: 'No verified Windows UBT/package/playtest evidence.' },
    productionMap: { status: 'unverified', label: 'W04 production map', detail: 'W04_AshenForest .umap is not verified.' }
  },
  blockers: [
    'Windows Unreal build/package/playtest evidence is missing',
    'W04 production map is not verified',
    '7 core production meshes remain unresolved',
    '2 approved master materials remain unresolved',
    '10 production AnimMontages remain unresolved',
    '16 audio payloads remain unresolved',
    '14 Niagara payloads remain unresolved'
  ],
  gates: [
    { name: 'Repository / static CI', status: 'passed', evidence: 'Verified CI evidence recorded in PROJECT_STATE.md' },
    { name: 'Core production assets', status: 'blocked', evidence: 'Production meshes remain unresolved' },
    { name: 'Animation validation', status: 'blocked', evidence: '10 production AnimMontages unresolved' },
    { name: 'Material validation', status: 'blocked', evidence: 'Approved master materials unresolved' },
    { name: 'Presentation payloads', status: 'blocked', evidence: '16 audio + 14 Niagara payloads unresolved' },
    { name: 'Production map validation', status: 'pending', evidence: 'W04_AshenForest .umap not verified' },
    { name: 'Windows build / package', status: 'pending', evidence: 'No runtime evidence yet' },
    { name: 'Shipping RC', status: 'blocked', evidence: 'Strict runtime/content gates are not satisfied' }
  ],
  w04: [
    { name: 'Main Menu', status: 'implemented' },
    { name: 'Intro', status: 'implemented' },
    { name: 'Wake Area', status: 'implemented' },
    { name: 'Movement / Combat', status: 'implemented' },
    { name: 'Memory Crystal', status: 'implemented' },
    { name: 'First Whisper', status: 'implemented' },
    { name: 'Ash Gate', status: 'implemented' },
    { name: 'Celestial Wolf', status: 'implemented' },
    { name: 'Bone Beast', status: 'implemented' },
    { name: 'Demo End', status: 'implemented' }
  ]
};

export function deriveSummary(state) {
  const hasRuntimeEvidence = state.evidence.windowsUnreal.status === 'passed';
  return {
    pipelineLabel: hasRuntimeEvidence ? 'Runtime evidence verified' : 'Runtime evidence pending',
    blockers: state.blockers,
    gatePasses: state.gates.filter(g => g.status === 'passed').length,
    gateTotal: state.gates.length,
    shipping: hasRuntimeEvidence && state.gates.every(g => g.status === 'passed')
      ? { status: 'passed', reason: 'All strict gates passed' }
      : { status: 'blocked', reason: 'Windows Unreal runtime evidence and strict production gates are incomplete' }
  };
}
