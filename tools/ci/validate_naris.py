from __future__ import annotations

import json
from pathlib import Path
import sys

from validate_unreal_source import validate_source

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "NARIS_MASTER",
    ROOT / "docs",
    ROOT / "data",
    ROOT / "worlds",
    ROOT / "unreal" / "NARIS_W04" / "NARIS_W04.uproject",
    ROOT / "docs" / "production" / "INTEGRATIONS_FIGMA_BLENDER_NEON.md",
    ROOT / "tools" / "blender" / "naris_export.py",
    ROOT / "backend" / "neon" / "schema" / "001_core.sql",
    ROOT / "integrations" / "figma" / "README.md",
    ROOT / "schemas" / "naris_blender_exchange.schema.json",
    ROOT / "unreal" / "NARIS_W04" / "Content" / "Python" / "naris_import_blender_exchange.py",
    ROOT / "tools" / "windows" / "Invoke-NarisBlenderUnrealSmoke.ps1",
    ROOT / "tools" / "windows" / "Invoke-NarisW04AuthoringBootstrap.ps1",
    ROOT / "unreal" / "NARIS_W04" / "Content" / "Python" / "naris_bootstrap_w04_smoke.py",
]

errors: list[str] = []
for path in REQUIRED:
    if not path.exists():
        errors.append(f"Missing required path: {path.relative_to(ROOT)}")

json_count = 0
for path in ROOT.rglob("*.json"):
    if any(part in {"node_modules", ".git", "Binaries", "Intermediate", "Saved", "DerivedDataCache"} for part in path.parts):
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
        json_count += 1
    except Exception as exc:
        errors.append(f"Invalid JSON: {path.relative_to(ROOT)} ({exc})")

uproject = ROOT / "unreal" / "NARIS_W04" / "NARIS_W04.uproject"
if uproject.exists():
    try:
        data = json.loads(uproject.read_text(encoding="utf-8"))
        if "FileVersion" not in data:
            errors.append("Unreal project does not contain FileVersion")
        enabled_plugins = {
            item.get("Name")
            for item in data.get("Plugins", [])
            if isinstance(item, dict) and item.get("Enabled") is True
        }
        for plugin in ("PythonScriptPlugin", "EditorScriptingUtilities"):
            if plugin not in enabled_plugins:
                errors.append(f"Unreal project must enable plugin: {plugin}")
    except Exception as exc:
        errors.append(f"Invalid Unreal .uproject: {exc}")

errors.extend(validate_source(ROOT / "unreal" / "NARIS_W04" / "Source"))

# Blender helper must at least parse as Python without importing Blender at CI time.
blender_script = ROOT / "tools" / "blender" / "naris_export.py"
if blender_script.exists():
    try:
        compile(blender_script.read_text(encoding="utf-8"), str(blender_script), "exec")
    except SyntaxError as exc:
        errors.append(f"Invalid Blender helper syntax: {exc}")

# Unreal Blender importer must parse without importing Unreal at CI time.
unreal_importer = ROOT / "unreal" / "NARIS_W04" / "Content" / "Python" / "naris_import_blender_exchange.py"
if unreal_importer.exists():
    try:
        compile(unreal_importer.read_text(encoding="utf-8"), str(unreal_importer), "exec")
    except SyntaxError as exc:
        errors.append(f"Invalid Unreal Blender importer syntax: {exc}")

# Blender exchange schema must preserve the production contract.
exchange_schema = ROOT / "schemas" / "naris_blender_exchange.schema.json"
if exchange_schema.exists():
    try:
        schema = json.loads(exchange_schema.read_text(encoding="utf-8"))
        required = set(schema.get("required", []))
        expected = {"schema", "asset_id", "blend_file", "objects", "issues", "status"}
        if not expected.issubset(required):
            errors.append("Blender exchange schema is missing required manifest fields")
    except Exception as exc:
        errors.append(f"Invalid Blender exchange schema: {exc}")

# Windows smoke test must bind Blender export to the canonical registry and Unreal importer.
smoke_ps1 = ROOT / "tools" / "windows" / "Invoke-NarisBlenderUnrealSmoke.ps1"
if smoke_ps1.exists():
    smoke = smoke_ps1.read_text(encoding="utf-8")
    for token in (
        "MASTER_ASSET_REGISTRY.json",
        "naris_import_blender_exchange.py",
        "NARIS_EXCHANGE_MANIFEST",
        "UnrealEditor-Cmd.exe",
    ):
        if token not in smoke:
            errors.append(f"Blender-Unreal smoke script missing contract token: {token}")

# W04 editor bootstrap must parse and target the configured prototype map.
bootstrap_script = ROOT / "unreal" / "NARIS_W04" / "Content" / "Python" / "naris_bootstrap_w04_smoke.py"
if bootstrap_script.exists():
    try:
        bootstrap_text = bootstrap_script.read_text(encoding="utf-8")
        compile(bootstrap_text, str(bootstrap_script), "exec")
        for token in (
            "/Game/NARIS/W04/Maps/W04_Prototype",
            "NarisWaystone",
            "NarisMemoryCrystal",
            "NarisAshGate",
            "CelestialWolf",
            "BoneBeastBoss",
        ):
            if token not in bootstrap_text:
                errors.append(f"W04 bootstrap missing contract token: {token}")
    except SyntaxError as exc:
        errors.append(f"Invalid W04 bootstrap Python syntax: {exc}")

engine_ini = ROOT / "unreal" / "NARIS_W04" / "Config" / "DefaultEngine.ini"
if engine_ini.exists():
    engine_text = engine_ini.read_text(encoding="utf-8")
    for token in (
        "EditorStartupMap=/Game/NARIS/W04/Maps/W04_Prototype",
        "GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype",
        "GlobalDefaultGameMode=/Script/NARIS_W04.NarisGameMode",
    ):
        if token not in engine_text:
            errors.append(f"DefaultEngine.ini missing W04 runtime setting: {token}")

# Neon migration contract: verify the core tables are declared and no connection secret is embedded.
neon_schema = ROOT / "backend" / "neon" / "schema" / "001_core.sql"
if neon_schema.exists():
    sql = neon_schema.read_text(encoding="utf-8")
    for table in (
        "naris_player",
        "naris_save_slot",
        "naris_inventory_item",
        "naris_entitlement",
        "naris_gameplay_event",
    ):
        if f"create table if not exists {table}" not in sql.lower():
            errors.append(f"Neon schema missing required table declaration: {table}")
    lowered = sql.lower()
    if "postgresql://" in lowered or "postgres://" in lowered:
        errors.append("Neon schema must not embed a database connection string")

# Figma handoff must point to the live file created for NARIS.
figma_readme = ROOT / "integrations" / "figma" / "README.md"
if figma_readme.exists():
    figma_text = figma_readme.read_text(encoding="utf-8")
    if "https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH" not in figma_text:
        errors.append("Figma handoff is missing the canonical NARIS design URL")
    for page in ("00_Foundations", "01_Game_UI", "02_Handoff"):
        if page not in figma_text:
            errors.append(f"Figma handoff missing page contract: {page}")

if errors:
    print("NARIS CI validation FAILED")
    for error in errors:
        print(f"::error::{error}")
    sys.exit(1)

print("NARIS CI validation PASSED")
print(f"Validated JSON files: {json_count}")
print("Validated Unreal project: unreal/NARIS_W04/NARIS_W04.uproject")
print("Validated Blender integration: tools/blender/naris_export.py")
print("Validated Neon schema contract: backend/neon/schema/001_core.sql")
print("Validated Figma handoff contract: integrations/figma/README.md")
print("Validated Blender exchange schema and Unreal import bridge")
print("Validated W04 Unreal editor bootstrap and runtime map settings")
