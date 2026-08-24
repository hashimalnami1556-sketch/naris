# NARIS CI/CD Status

## Configured

- GitHub repository: `hashimalnami1556-sketch/naris`
- Repository validation workflow: `.github/workflows/naris-ci.yml`
- Codex PR preflight: `.github/workflows/codex-pr-check.yml`
- Codex/GitHub operating guide: `docs/CODEX_CLOUD_SETUP.md`
- Unreal project: `unreal/NARIS_W04/NARIS_W04.uproject`
- MCP build: `mcp/npm run build`
- Self-hosted Unreal target: `[self-hosted, windows, unreal]`

## Remaining account/machine configuration

These cannot be safely completed by a repository write alone:

1. Authorize the NARIS repository in the user's Codex Cloud environment.
2. Register a Windows machine as a GitHub Actions self-hosted runner.
3. Install the required Unreal Engine version on that runner.
4. Set `UNREAL_ENGINE_ROOT` on the runner.
5. Add branch protection/rulesets requiring CI before merging to `main`.

## Operating rule

All Codex implementation work should target a branch and open a Pull Request. `main` is the integration branch. CI is the gate.
