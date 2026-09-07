# NARIS — Neon MCP Integration Policy

## Purpose
Use Neon as an optional development/test persistence layer without coupling the browser runtime to database credentials.

## Rules
- Neon MCP is a development/testing integration, not a production database-agent control plane.
- Never ship Neon MCP credentials or privileged database access in the browser bundle.
- Prefer a project-scoped, read-only MCP configuration for inspection tasks.
- Schema changes should be reviewed and applied through controlled migrations.
- Production gameplay persistence should go through an authenticated application API, not directly through MCP.
- Keep player/PII data out of MCP test environments; use anonymized fixtures.
- The hosted Neon MCP transport is Streamable HTTP at `https://mcp.neon.tech/mcp`; the older `/sse` endpoint is deprecated and scheduled for retirement on/after October 1, 2026.

## NARIS application boundary

```text
Babylon.js Browser Runtime
        |
        v
NARIS Application API
        |
        +---- gameplay/session persistence
        |
        +---- authenticated player profile
        |
        v
      Neon Postgres

Developer / CI
        |
        v
Neon MCP (scoped, reviewed, non-production)
```

## Future persistence tables
- `player_profiles`
- `save_slots`
- `save_revisions`
- `unlocked_realms`
- `quest_progress`
- `inventory_items`
- `achievement_unlocks`
- `telemetry_sessions`

The current vertical slice remains localStorage-first. Neon is an extension point for account-backed saves and analytics after the browser gameplay loop is stable.
