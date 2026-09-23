# Shared knowledge sources

Updated: 2026-09-23. This is a routing layer over existing repository documents, not a second GDD.

| Responsibility | Canonical owner | Evidence meaning |
|---|---|---|
| Shared agent policy | [AGENTS](../../AGENTS.md) | Operating guide |
| Current objective and handoff | [Project state](../../PROJECT_STATE.md) | Current work only |
| Scope and identity | [README](../../README.md) | Existing project baseline |
| Directory governance | [Repository map](../REPOSITORY_MAP.md) | Existing taxonomy |
| Production readiness | [Production status](../PRODUCTION_STATUS.md) | Release gates and evidence |
| Remaining implementation work | [Gap register](../PROJECT_GAP_REGISTER.md) | Backlog, not completed execution |
| Asset identities and current fields | [Master registry](../../data/MASTER_ASSET_REGISTRY.json) | Machine-readable source |
| Production gates | [Pipeline](../MASTER_PRODUCTION_PIPELINE.md) | Promotion rules |
| Engine selection | [Project descriptor](../../unreal/NARIS_W04/NARIS_W04.uproject) | Checked-in setting, not build proof |
| Implemented runtime | [Unreal source](../../unreal/NARIS_W04/Source/) | Source code, not playtest proof |
| World generation | [AssetForge contract](ASSETFORGE_WORLDGEN.md) | Tool scope and limitations |
| Durable decisions | [Decision index](decisions/index.md) | Accepted changes and rationale |
| Work ownership | [Work index](work/index.md) | Claims, progress and handoffs |

## Existing knowledge adoption
Keep existing docs, NARIS_MASTER, data and Unreal ownership. Historical/source material remains under DOCUMENTS and migration; no bulk migration or second vault was created. Chat supplies intent, never evidence that code ran. Missing attachments stay unavailable until bytes are received and inspected.

## Lifecycle
Plain Markdown is supported by the project lint profile. New work records carry an updated date, decision owner, executing agent, scope, completed work, blockers and next step. Decisions must distinguish proposal from accepted change. Superseded notes identify their replacement and leave active routing; historical rationale remains in Git or the work archive. No synthetic product decisions are created to populate indexes.

## Hosts
Codex enters through root AGENTS.md. Claude Code has a thin @AGENTS.md adapter. Both must work from the same repository checkout or synchronize commits. Automatic Claude loading and plugin availability require an actual Claude Code test and are currently unverified.
