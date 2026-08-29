# NARES MASTER — Production & Asset Delivery Bible
## الإصدار 1.0 — Studio Production Standard

> المرجع الإلزامي لتسليم الأصول. لا يُعامل الأصل كملف منفرد؛ بل كـ Asset Package + Metadata + Dependencies + Runtime Version + QA + Documentation.

## 01 — نظام تعريف الأصول
كل Asset يجب أن يمتلك: Asset ID، Asset Type، Department، Owner، Status، Priority، Version، Source، Runtime، Dependencies، QA، Approval.

**Status:** IDEA / CONCEPT / CONCEPT_APPROVED / HIGH_POLY / LOW_POLY / UV / TEXTURE / RIG / ANIMATION / ENGINE_IMPORT / MATERIAL / LOD / COLLISION / LIGHTING_VFX / GAMEPLAY_INTEGRATION / QA / APPROVED / FINAL.

**Priority:** P0 / P1 / P2 / P3.

## 02 — Character Package
```text
CHR_NARES_001/
├── 01_CONCEPT/{Turnaround,Expressions,Costume,Silhouette,Color}
├── 02_HIGH_POLY/
├── 03_LOW_POLY/
├── 04_UV/
├── 05_TEXTURES/
├── 06_RIG/
├── 07_ANIMATION/
├── 08_MATERIALS/
├── 09_LOD/
├── 10_ENGINE/
├── 11_DOCUMENTATION/
└── 12_QA/
```

## 03 — Naming Convention
**Meshes:** `SK_Nares_Body`, `SK_Nares_Head`, `SK_Nares_Cloth`, `SK_Nares_Armor`  
**Materials:** `M_Nares_Master`, `MI_Nares_Skin`, `MI_Nares_Cloth`, `MI_Nares_Metal`  
**Textures:** `T_Nares_Body_BC/N/M/R/AO/ID`  
**Animation:** `AN_Nares_Idle`, `AN_Nares_Walk`, `AN_Nares_Run`, `AN_Nares_Sprint`, `AN_Nares_Jump`, `AN_Nares_Land`, `AN_Nares_Attack_Light_01`, `AN_Nares_Attack_Heavy_01`, `AN_Nares_Block`, `AN_Nares_Parry`, `AN_Nares_Dodge`, `AN_Nares_Hit`, `AN_Nares_Death`.

## 04 — Animation Standard
**Locomotion:** Idle, Walk, Run, Sprint, Strafe_L, Strafe_R, Backward.  
**Combat:** LightAttack_01-03, HeavyAttack_01-02, Block, Parry, Counter, Dodge, Dodge_Roll.  
**Reaction:** Hit_Front, Hit_Back, Hit_Left, Hit_Right, Knockdown, GetUp, Death_01-02.  
**Interaction:** Interact, PickUp, Open, Close, Push, Pull, Climb, Vault, Jump, Land.

## 05 — Weapon Package
```text
WPN_Sword_001/
├── CONCEPT/ ├── HIGH_POLY/ ├── LOW_POLY/ ├── UV/
├── TEXTURES/ ├── MATERIAL/ ├── RIG/ ├── ANIMATION/
├── VFX/ ├── AUDIO/ ├── ENGINE/ └── QA/
```
Required references: Full View, Side View, Detail View, Scale, Grip, Material, Damage/Gameplay, Sheathing, Animation, VFX, Audio.

## 06 — Environment Modular Kit
```text
ENV_DESERT_CITY/
├── Architecture/{Walls,Floors,Roofs,Doors,Windows,Arches,Stairs}
├── Props/{Barrels,Crates,Lamps,Furniture,Decorations}
├── Nature/{Trees,Plants,Rocks,Sand}
├── Materials/ ├── VFX/ ├── Lighting/ └── Engine/
```
البيئة Modular System وليست مجموعة Meshes منفصلة.

## 07 — Texture / LOD / Collision
**PBR:** BC, N, R, M, AO, H, E, ID. لا Texture منفردة بلا ارتباط.  
**LOD:** LOD0 Hero، LOD1 High، LOD2 Medium، LOD3 Low، LOD4 Optional. يحدد Technical Art القرار وفق Screen Size وPolygon Count وDistance وPlatform وImportance وPerformance Budget.  
**Collision:** `UCX_AssetName_01` وما بعده؛ اختبار Player / Projectile / Interaction / Navigation / Physics.

## 08 — Master Material
```text
M_MASTER_SURFACE
├── MI_STONE
├── MI_METAL
├── MI_WOOD
├── MI_CLOTH
├── MI_SKIN
└── MI_LEATHER
```
Parameters: Base Color, Roughness, Metallic, Normal Strength, AO, Emissive, Detail Scale, Tiling, Dirt, Wetness, Damage.

## 09 — UI / UX
Design Language موحد لـ Character Select وProfile وEquipment وInventory وSkills وQuests وJournal وCrafting وReputation وMap وSettings. Deliverables: Wireframe، High Fidelity، Component Library، Typography، Icons، Buttons، Panels، Cards، Tabs، Notifications، HUD، Menus، Controller/Keyboard Navigation، Responsive Layout.

## 10 — VFX / Audio
VFX metadata: VFX_ID, SOURCE, MATERIAL, PARTICLE, LIGHT, SOUND, GAMEPLAY_EVENT, PERFORMANCE_BUDGET.  
Audio: `SFX/{Character,Weapons,Environment,UI,Combat,Interaction,VFX}`, `MUSIC/{Exploration,Combat,Boss,Cinematic,Ambient}`, `VO/{Characters,Quests,Combat,Cinematics}`.

## 11 — Level / Quest
Level pipeline: BLOCKOUT → GAMEPLAY PASS → COMBAT PASS → QUEST PASS → ART PASS → LIGHTING PASS → VFX PASS → AUDIO PASS → OPTIMIZATION → QA → FINAL.  
Quest package: `QUEST_ID/Design/Dialogue/Objectives/Rewards/NPC/Locations/Cinematics/VO/UI/QA`; مثال `QST_DESERT_001`.

## 12 — Technical Documentation
لكل نظام: ما الأصل؟ من أنشأه؟ المصدر؟ Dependencies؟ أين يستخدم؟ إعدادات المحرك؟ Performance Budget؟ طريقة التحديث؟ المشاكل المعروفة؟ المسؤول؟

## 13 — Inventory
السجل المركزي يجب أن يربط ID، Asset، Department، Status، Version، Owner، QA، Source، Runtime، Dependencies، Approval، Linear Issue وCI evidence.

## 14 — QA Gate
**Visual:** مطابقة Concept، النسب، المواد، الألوان.  
**Technical:** Naming، Pivot، Scale، Rotation، UV، Collision، LOD.  
**Engine:** Import، Material، Animation، Blueprint، Performance.  
**Final:** No Missing Textures، Broken References، Duplicate Assets، Naming Errors، Unexpected Warnings.

## 15 — Version / Approval
الإصدار: `AssetName_v001 → v002 → v003 → AssetName_FINAL` ولا تحذف النسخ القديمة مباشرة.  
Approval: Artist → Lead → Art Director → Technical Art → Game Integration → QA → FINAL.

## 16 — Definition of Done
لا يعتبر الأصل DONE حتى: Concept Approved، Model، UV، Textures، Material، Rig، Animation، LOD، Collision، Engine Import، Gameplay Integration، Performance، QA، Documentation، Final Approval كلها ناجحة.

## 17 — Master Production Loop
`IDEA → CONCEPT → DESIGN REVIEW → 3D → TEXTURE → RIG → ANIMATION → TECH ART → UNREAL → GAMEPLAY → VFX + AUDIO → LIGHTING → OPTIMIZATION → QA → APPROVAL → SHIP`

## Golden Rule
**لا يتم تسليم Asset باعتباره ملفاً؛ يتم تسليمه كحزمة إنتاج قابلة للتتبع والتشغيل والاختبار.**
