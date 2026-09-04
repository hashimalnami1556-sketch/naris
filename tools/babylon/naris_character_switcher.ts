import { Engine, Scene, ArcRotateCamera, HemisphericLight, Vector3, Color4, MeshBuilder, StandardMaterial, Color3 } from '@babylonjs/core';

export type CharacterPreset = {
  id: string;
  label: string;
  accent: Color3;
  height: number;
};

export const NARIS_CHARACTER_PRESETS: CharacterPreset[] = [
  { id: 'NARIS-W04-CHR-HERO-0001', label: 'Ashen Vessel', accent: new Color3(1.0, 0.28, 0.04), height: 1.83 },
  { id: 'NARIS-W04-CHR-ASHWANDERER-0001', label: 'Ash Wanderer', accent: new Color3(0.75, 0.12, 0.04), height: 1.82 },
  { id: 'NARIS-W07-CHR-MARSHSEER-0001', label: 'Marsh Seer', accent: new Color3(0.05, 0.95, 0.85), height: 1.78 },
  { id: 'NARIS-W08-CHR-CASTLEWARDEN-0001', label: 'Castle Warden', accent: new Color3(0.45, 0.52, 0.65), height: 1.95 }
];

export class NarisProceduralCharacterFactory {
  constructor(private readonly scene: Scene) {}

  build(preset: CharacterPreset) {
    const root = MeshBuilder.CreateBox(`${preset.id}_ROOT`, { width: 0.001, height: 0.001, depth: 0.001 }, this.scene);
    root.isVisible = false;

    const body = MeshBuilder.CreateCapsule(`${preset.id}_BODY`, { height: preset.height * 0.52, radius: 0.26 }, this.scene);
    body.parent = root;
    body.position.y = preset.height * 0.43;

    const head = MeshBuilder.CreateSphere(`${preset.id}_HEAD`, { diameter: 0.38 }, this.scene);
    head.parent = root;
    head.position.y = preset.height * 0.76;

    const material = new StandardMaterial(`${preset.id}_MAT`, this.scene);
    material.diffuseColor = new Color3(0.055, 0.045, 0.05);
    material.emissiveColor = preset.accent.scale(0.35);
    body.material = material;
    head.material = material;

    root.metadata = {
      narisAssetId: preset.id,
      productionStatus: 'procedural_preview',
      sockets: ['hand_r', 'hand_l', 'back', 'head', 'root'],
      lod: [0, 1, 2],
      sourceOfTruth: 'data/asset_registry/batch_09_asset_manifest.json'
    };
    return root;
  }
}

export function createNarisPreview(canvas: HTMLCanvasElement) {
  const engine = new Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });
  const scene = new Scene(engine);
  scene.clearColor = new Color4(0.006, 0.008, 0.012, 1);
  const camera = new ArcRotateCamera('NARIS_PREVIEW_CAMERA', -Math.PI / 2, Math.PI / 2.4, 5.2, new Vector3(0, 0.9, 0), scene);
  camera.attachControl(canvas, true);
  new HemisphericLight('NARIS_PREVIEW_LIGHT', new Vector3(0, 1, 0), scene).intensity = 1.2;

  const factory = new NarisProceduralCharacterFactory(scene);
  let index = 0;
  let current = factory.build(NARIS_CHARACTER_PRESETS[index]);

  const switchCharacter = (delta = 1) => {
    current.dispose();
    index = (index + delta + NARIS_CHARACTER_PRESETS.length) % NARIS_CHARACTER_PRESETS.length;
    current = factory.build(NARIS_CHARACTER_PRESETS[index]);
  };

  engine.runRenderLoop(() => scene.render());
  window.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') switchCharacter(1);
    if (event.key === 'ArrowLeft') switchCharacter(-1);
  });

  return { engine, scene, switchCharacter };
}
