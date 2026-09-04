import * as BABYLON from "https://cdn.babylonjs.com/babylon.js";

/**
 * CALL OF NARIS — procedural Babylon.js asset factory.
 * Preview/build layer only: canonical production assets remain source-controlled
 * and final hero assets are intended for Unreal Engine import.
 */

export const NARIS_ASSET_IDS = Object.freeze({
  ashWanderer: "NARIS-W04-CHR-ASHWANDERER-0001",
  marshSeer: "NARIS-W07-CHR-MARSHSEER-0001",
  castleWarden: "NARIS-W08-CHR-CASTLEWARDEN-0001",
  translucentHero: "NARIS-W04-CHR-HERO-TRANSLUCENT-0001",
  gateGuardian: "NARIS-W04-ENM-GATEGUARDIAN-0001",
  waystone: "NARIS-W04-PRP-WAYSTONE-0001",
  holyPortal: "NARIS-W04-PRP-HOLYPORTAL-0001",
  stoneTile: "NARIS-W04-MAT-STONETILE-0001"
});

const COLORS = {
  fire: new BABYLON.Color3(1.0, 0.32, 0.08),
  violet: new BABYLON.Color3(0.48, 0.28, 1.0),
  cyan: new BABYLON.Color3(0.0, 0.88, 1.0),
  gold: new BABYLON.Color3(1.0, 0.72, 0.08),
  emerald: new BABYLON.Color3(0.05, 0.8, 0.35),
  steel: new BABYLON.Color3(0.32, 0.38, 0.45),
  obsidian: new BABYLON.Color3(0.025, 0.03, 0.045)
};

function mat(name, color, scene, alpha = 1, emissive = 0.0) {
  const m = new BABYLON.StandardMaterial(name, scene);
  m.diffuseColor = color;
  m.emissiveColor = color.scale(emissive);
  m.specularColor = new BABYLON.Color3(0.18, 0.2, 0.24);
  m.alpha = alpha;
  if (alpha < 1) {
    m.transparencyMode = BABYLON.Material.MATERIAL_ALPHABLEND;
    m.backFaceCulling = false;
  }
  return m;
}

function etherealMat(name, color, scene) {
  const m = mat(name, color, scene, 0.42, 0.65);
  m.alphaMode = BABYLON.Engine.ALPHA_COMBINE;
  m.useSpecularOverAlpha = true;
  return m;
}

function primitiveCharacter(name, scene, palette, options = {}) {
  const root = new BABYLON.TransformNode(name, scene);
  const bodyMat = options.ethereal ? etherealMat(`${name}_body`, palette, scene) : mat(`${name}_body`, palette, scene, 1, 0.08);
  const metalMat = options.ethereal ? etherealMat(`${name}_metal`, COLORS.steel, scene) : mat(`${name}_metal`, COLORS.steel, scene, 1, 0.02);

  const torso = BABYLON.MeshBuilder.CreateCylinder(`${name}_torso`, {height: 1.35, diameterTop: 0.62, diameterBottom: 0.86, tessellation: 12}, scene);
  torso.position.y = 1.85;
  torso.material = bodyMat;
  torso.parent = root;

  const head = BABYLON.MeshBuilder.CreateSphere(`${name}_head`, {diameter: 0.52, segments: 12}, scene);
  head.position.y = 2.82;
  head.material = bodyMat;
  head.parent = root;

  const hip = BABYLON.MeshBuilder.CreateBox(`${name}_hip`, {width: 0.72, height: 0.36, depth: 0.42}, scene);
  hip.position.y = 1.18;
  hip.material = metalMat;
  hip.parent = root;

  for (const side of [-1, 1]) {
    const leg = BABYLON.MeshBuilder.CreateCylinder(`${name}_leg_${side}`, {height: 1.25, diameter: 0.24, tessellation: 10}, scene);
    leg.position.set(side * 0.23, 0.58, 0);
    leg.material = metalMat;
    leg.parent = root;
    const arm = BABYLON.MeshBuilder.CreateCylinder(`${name}_arm_${side}`, {height: 1.25, diameter: 0.19, tessellation: 10}, scene);
    arm.rotation.z = side * -0.12;
    arm.position.set(side * 0.55, 1.93, 0);
    arm.material = metalMat;
    arm.parent = root;
  }

  if (options.hood) {
    const hood = BABYLON.MeshBuilder.CreateCylinder(`${name}_hood`, {height: 0.5, diameterTop: 0.68, diameterBottom: 0.9, tessellation: 16}, scene);
    hood.position.y = 2.65;
    hood.material = bodyMat;
    hood.parent = root;
  }

  const aura = BABYLON.MeshBuilder.CreateTorus(`${name}_aura`, {diameter: 1.15, thickness: 0.035, tessellation: 32}, scene);
  aura.position.y = 1.2;
  aura.rotation.x = Math.PI / 2;
  aura.material = options.ethereal ? etherealMat(`${name}_aura_mat`, palette, scene) : mat(`${name}_aura_mat`, palette, scene, 0.5, 0.7);
  aura.parent = root;

  root.metadata = {assetId: options.assetId, role: options.role, procedural: true};
  return root;
}

export function createAshWanderer(scene) {
  return primitiveCharacter("AshWanderer", scene, COLORS.fire, {
    assetId: NARIS_ASSET_IDS.ashWanderer, role: "DPS / Explorer", hood: true
  });
}

export function createMarshSeer(scene) {
  return primitiveCharacter("MarshSeer", scene, COLORS.cyan, {
    assetId: NARIS_ASSET_IDS.marshSeer, role: "Support / Caster", hood: true
  });
}

export function createCastleWarden(scene) {
  return primitiveCharacter("CastleWarden", scene, COLORS.gold, {
    assetId: NARIS_ASSET_IDS.castleWarden, role: "Tank / Guardian"
  });
}

export function createTranslucentHero(scene) {
  return primitiveCharacter("TranslucentHero", scene, COLORS.cyan, {
    assetId: NARIS_ASSET_IDS.translucentHero, role: "Echo / Spirit State", ethereal: true, hood: true
  });
}

export function createGateGuardian(scene) {
  const root = primitiveCharacter("GateGuardian", scene, COLORS.fire, {
    assetId: NARIS_ASSET_IDS.gateGuardian, role: "Elite Gate Enemy", ethereal: true
  });
  const horns = [];
  for (const side of [-1, 1]) {
    const horn = BABYLON.MeshBuilder.CreateCylinder(`GateGuardian_horn_${side}`, {height: 0.75, diameterTop: 0.04, diameterBottom: 0.18, tessellation: 10}, scene);
    horn.position.set(side * 0.22, 3.18, 0);
    horn.rotation.z = side * -0.28;
    horn.material = etherealMat(`GateGuardian_horn_mat_${side}`, COLORS.fire, scene);
    horn.parent = root;
    horns.push(horn);
  }
  return root;
}

export function createWaystone(scene) {
  const root = new BABYLON.TransformNode("Waystone", scene);
  const base = BABYLON.MeshBuilder.CreateCylinder("WaystoneBase", {height: 0.55, diameter: 1.15, tessellation: 8}, scene);
  base.material = mat("WaystoneStone", COLORS.steel, scene, 1, 0.02);
  base.parent = root;
  const crystal = BABYLON.MeshBuilder.CreatePolyhedron("WaystoneCrystal", {type: 1, size: 0.78}, scene);
  crystal.position.y = 0.68;
  crystal.rotation.y = 0.35;
  crystal.material = etherealMat("WaystoneCrystalMat", COLORS.cyan, scene);
  crystal.parent = root;
  root.metadata = {assetId: NARIS_ASSET_IDS.waystone, type: "save_point"};
  return root;
}

export function createHolyPortal(scene) {
  const root = new BABYLON.TransformNode("HolyPortal", scene);
  const frame = BABYLON.MeshBuilder.CreateTorus("HolyPortalFrame", {diameter: 3.2, thickness: 0.24, tessellation: 48}, scene);
  frame.scaling.y = 1.35;
  frame.material = etherealMat("HolyPortalFrameMat", COLORS.gold, scene);
  frame.parent = root;
  const core = BABYLON.MeshBuilder.CreateDisc("HolyPortalCore", {radius: 1.48, tessellation: 64}, scene);
  core.rotation.x = Math.PI / 2;
  core.material = etherealMat("HolyPortalCoreMat", COLORS.cyan, scene);
  core.parent = root;
  root.metadata = {assetId: NARIS_ASSET_IDS.holyPortal, type: "transition_gate"};
  return root;
}

export function createStoneTileMaterial(scene) {
  const m = new BABYLON.StandardMaterial("AshenStoneTile", scene);
  m.diffuseColor = new BABYLON.Color3(0.17, 0.18, 0.2);
  m.bumpTexture = new BABYLON.DynamicTexture("StoneTileProceduralNormal", {width: 256, height: 256}, scene, false);
  const ctx = m.bumpTexture.getContext();
  ctx.fillStyle = "#808080";
  ctx.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 256; y += 32) {
    for (let x = 0; x < 256; x += 32) {
      ctx.strokeStyle = ((x / 32 + y / 32) % 2 === 0) ? "#b0b0b0" : "#505050";
      ctx.lineWidth = 3;
      ctx.strokeRect(x + 2, y + 2, 28, 28);
    }
  }
  m.bumpTexture.update();
  m.bumpTexture.uScale = 4;
  m.bumpTexture.vScale = 4;
  m.specularPower = 48;
  m.metadata = {assetId: NARIS_ASSET_IDS.stoneTile, tileable: true, targetResolution: "4096"};
  return m;
}

export function createAssetById(assetId, scene) {
  const factory = {
    [NARIS_ASSET_IDS.ashWanderer]: createAshWanderer,
    [NARIS_ASSET_IDS.marshSeer]: createMarshSeer,
    [NARIS_ASSET_IDS.castleWarden]: createCastleWarden,
    [NARIS_ASSET_IDS.translucentHero]: createTranslucentHero,
    [NARIS_ASSET_IDS.gateGuardian]: createGateGuardian,
    [NARIS_ASSET_IDS.waystone]: createWaystone,
    [NARIS_ASSET_IDS.holyPortal]: createHolyPortal
  }[assetId];
  if (!factory) throw new Error(`Unknown NARIS asset id: ${assetId}`);
  return factory(scene);
}
