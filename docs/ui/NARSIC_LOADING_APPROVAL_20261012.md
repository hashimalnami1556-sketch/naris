# NARSIC — Approved Ash Gate loading / startup design

**Decision:** Adopt the latest user-approved image, the circular Ash Gate transit dial,
dark ruined citadel, mist, low-saturation blue/charcoal atmosphere and restrained ember/bronze highlights.

**Product title:** `NARSIC` exactly. Technical `NARIS_*` module identifiers stay unchanged for compatibility.

## Implementation

- The binary is named `NARSIC_Transit_Approved.png` and SHA-256-verified by the installer.
- In Unreal 5.7 `MoviePlayer` renders a non-interactive Slate screen during blocking `LoadMap`; ordinary UMG cannot reliably tick while the game thread is blocked.
- The map-load lifecycle is bound through `FCoreUObjectDelegates::PreLoadMap`.
- The loading widget terminates automatically when actual map loading completes.
- An animated **indeterminate** throbber indicates loading. Never turn the **62% printed in the original key art** into a false runtime claim.
- Windows startup splash uses a BMP exported losslessly from the approved image.
- Art file stages as **NonUFS** so Slate can read it as a file in packaged Windows builds.

## Storage and deployment

The full-resolution PNG is provided in `NARSIC_LOADING_INSTALL_PACK.zip` in the conversation.
The source repository stores C++ integration, packaging configuration, integrity manifest,
and installer at `tools/install_narsic_transit.py`.
The PNG is not claimed to be inside GitHub until a binary upload is actually confirmed.

On the original AsusRog Unreal project:

```powershell
py tools/install_narsic_transit.py --project "C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57" --image "PATH_TO\NARSIC_Transit_Approved.png"
```

Or use the bundled `scripts/install_narsic_loading.py` for the full package + splash backup behavior.

## Acceptance

1. Compile `NARIS_W04` / `NARIS` in Unreal 5.7 on the workstation.
2. Package Windows Development; verify loose PNG exists in staged Content.
3. Verify visible startup splash plus **real** LoadMap transition.
4. Inspect alignment at 16:9, 21:9, 32:9.
5. No static painted percentage should be mistaken for measured load progress.
6. No black screen, blocking firewall window, or Lighting Needs Rebuild overlay.
7. Keep game input disabled until world load actually finishes.

## State

- Approval and repository integration: **source committed**.
- Art payload: **delivered in installer bundle**.
- AsusRog device reported offline during this update.
- Compile/package/runtime screenshots: **pending**, not claimed successful.
