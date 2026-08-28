# NARIS Connector Integration Matrix

## Purpose

Define one production contract across visual generation, design, asset conversion, video, documentation, security, source control, analytics, and game runtime.

## Canonical flow

`Brief → Concept → Design Review → Asset ID → Source Asset → 3D/Texture → Validation → Unreal Import → Optimization → QA → Release`

## Responsibilities

| System | NARIS responsibility | Output | Gate |
|---|---|---|---|
| GitHub | System of record, source control, schemas, CI, release history | specs, registries, code, workflows | required |
| Game Studio | Game architecture, gameplay, runtime and QA routing | playable systems, tests | required |
| Figma / Product Design | UX/UI, HUD, menus, interaction flows | design specs | required for UI |
| Adobe / Acrobat / Express | concept art, source visuals, controlled PDFs, marketing | source art, bibles, campaign assets | approval |
| Higgsfield | cinematic concept/video and visual iteration | shots, keyframes, video concepts | creative review |
| OpenArt | concept exploration and reference generation | character/environment concepts | concept gate |
| Apixel | image generation and graphic variants | key art, icons, promotional graphics | visual QA |
| to3D | 2D-to-3D prototyping | GLB/glTF/3D source candidates | technical-art gate |
| Amazing Drawing | rapid diagrams and gameplay/world sketches | maps, flows, combat diagrams | design review |
| Visla Video Maker | narrated marketing/production video | trailer drafts, explainers | editorial review |
| VideoZero | explanatory/gameplay visualization | technical/gameplay videos | review |
| Photo9 | physical/photo-book style presentation when required | art-book references | optional |
| WalkMyPlan | spatial/floor-plan visualization | interior/layout references | environment review |
| Slack | production communication and review routing | decisions, approvals, blockers | traceability |
| Bitdefender | external link/file reputation checks | security decision | security gate |
| Photon Commerce | document/data extraction when source documents contain structured production information | structured records | data QA |
| Data Analytics | KPI/telemetry analysis | balance and retention insights | playtest gate |
| 01 Superdesign / Designly | supplemental design ideation where available | design references | review |

## Connector rule

A connector is an accelerator, never the authoritative record. Every accepted output must receive a NARIS Asset ID and be represented in GitHub before it can become a release dependency.

## Asset ID

`NARIS-W<world>-<domain>-<type>-<sequence>`

Examples:
- `NARIS-W04-CHR-HERO-0001`
- `NARIS-W04-WPN-MACE-0001`
- `NARIS-W06-ENV-GEO-0001`
- `NARIS-W08-VFX-NIAGARA-0001`

## Failure policy

If a connector is unavailable, rate-limited, lacks credits, or cannot export the required production format, the pipeline records the status as `BLOCKED` and continues with the next independent production stage. No fake asset or fabricated connector result is accepted.

## Required metadata

`asset_id`, `name`, `world`, `domain`, `type`, `source`, `version`, `stage`, `format`, `owner`, `unreal_path`, `lod_policy`, `texture_policy`, `qa_state`, `approval_state`.
