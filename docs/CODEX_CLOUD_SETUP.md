# NARIS — Codex Cloud + GitHub + CI/CD

## Target workflow

Codex Cloud → feature branch → Pull Request → GitHub Actions → validation/build → review → main.

## Repository

`hashimalnami1556-sketch/naris`

## Branch policy

- `main`: protected production/integration branch.
- `codex/*`: automated development branches.
- `feature/*`: human feature branches.

Do not push generated Unreal build output to `main`.

## Codex Cloud setup

1. Connect GitHub to Codex using the GitHub account that owns or has write access to the NARIS repository.
2. Grant Codex access to `hashimalnami1556-sketch/naris`.
3. Select the repository and `main` as the base branch.
4. Use PR-based changes rather than direct production edits.
5. Require CI to pass before merging.

## Standard Codex task

Use a task such as:

> Work on `hashimalnami1556-sketch/naris`. Create a `codex/*` branch. Implement the requested change. Run repository validation and MCP build. If Unreal build validation is available, run it. Fix failures. Commit the changes and open a PR against `main`. Do not modify generated Unreal folders.

## CI stages

1. Repository structure and JSON validation.
2. MCP TypeScript build.
3. Unreal `.uproject` integrity validation.
4. Full Unreal build on a self-hosted Windows runner labeled `self-hosted, windows, unreal` when manually dispatched.

## Self-hosted Unreal runner

The Windows machine running Unreal Engine must have:

- GitHub Actions runner installed.
- Labels: `self-hosted`, `windows`, `unreal`.
- Unreal Engine installed.
- `UNREAL_ENGINE_ROOT` configured as a runner environment variable.
- Permission to access the repository.

The runner should have enough disk space for Unreal Intermediate/DerivedDataCache and project compilation.

## Security

Never commit:

- GitHub tokens
- Codex/API keys
- Unreal marketplace credentials
- `.env` files containing secrets
- signing certificates/private keys

Use GitHub Actions secrets or environment variables instead.

## Large assets

Use Git LFS for `.uasset`, `.umap`, `.fbx`, `.blend`, audio/video, PSD, EXR and other large binary assets. Keep generated folders out of Git.
