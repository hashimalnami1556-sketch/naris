#!/usr/bin/env python3
"""Deterministic validation for the canonical NARIS asset manifest."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.0.0"
ASSET_ID = re.compile(r"^NARIS-[A-Z0-9]+-[A-Z0-9-]+$")
TYPES = {"character","weapon","environment","prop","vfx","ui","audio","scene","animation","material","texture","data"}
STATUSES = {"planned","source","processing","validated","integrated","blocked"}


def fail(message: str) -> int:
    print(f"NARIS_MANIFEST_FAIL: {message}")
    return 1


def main() -> int:
    path = ROOT / "data" / "naris-asset-manifest.json"
    if not path.exists():
        return fail(f"missing {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"invalid JSON: {exc}")
    if data.get("schemaVersion") != SCHEMA_VERSION:
        return fail(f"schemaVersion must be {SCHEMA_VERSION}")
    assets = data.get("assets")
    if not isinstance(assets, list):
        return fail("assets must be an array")
    seen = set()
    for i, asset in enumerate(assets):
        if not isinstance(asset, dict):
            return fail(f"assets[{i}] must be an object")
        for key in ("assetId", "name", "type", "sourcePath", "status"):
            if not isinstance(asset.get(key), str) or not asset[key].strip():
                return fail(f"assets[{i}].{key} is required")
        aid = asset["assetId"]
        if not ASSET_ID.fullmatch(aid):
            return fail(f"assets[{i}].assetId has invalid format: {aid}")
        if aid in seen:
            return fail(f"duplicate assetId: {aid}")
        seen.add(aid)
        if asset["type"] not in TYPES:
            return fail(f"unsupported type for {aid}: {asset['type']}")
        if asset["status"] not in STATUSES:
            return fail(f"unsupported status for {aid}: {asset['status']}")
    print(f"NARIS_MANIFEST_OK: {len(assets)} assets validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
