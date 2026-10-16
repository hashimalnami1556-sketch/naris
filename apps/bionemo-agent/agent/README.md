# Agent layer

The agent layer deliberately separates intent routing from provider calls.

Initial routes:

- `structure_prediction` → OpenFold3
- `molecular_docking` → DiffDock/Boltz2 (next)
- `protein_binder_design` → RFdiffusion/ProteinMPNN/Boltz2 (next)

Provider adapters remain behind stable workflow contracts so NIM hosting can change without rewriting the UI.