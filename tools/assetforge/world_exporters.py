"""CALL OF NARIS — AssetForge raster exporters.

Standard-library-only exporters for deterministic world-generator outputs.
R16 uses big-endian unsigned 16-bit samples, suitable as an engine-neutral
Landscape interchange source. PGM masks are intentionally simple grayscale
source masks; Unreal/DCC tooling may transcode them to PNG/texture assets.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Sequence


def _validate_square(grid: Sequence[Sequence[object]]) -> int:
    size = len(grid)
    if size < 1 or any(len(row) != size for row in grid):
        raise ValueError("grid must be non-empty and square")
    return size


def export_heightmap_r16(heightmap: Sequence[Sequence[float]], output: Path) -> None:
    """Write normalized [0,1] heights as big-endian uint16 samples."""
    _validate_square(heightmap)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fh:
        for row in heightmap:
            for value in row:
                v = max(0.0, min(1.0, float(value)))
                fh.write(struct.pack(">H", round(v * 65535.0)))


def export_biome_masks_pgm(
    biomes: Sequence[Sequence[str]], output_dir: Path
) -> list[Path]:
    """Write one binary PGM mask per biome present in the grid."""
    size = _validate_square(biomes)
    output_dir.mkdir(parents=True, exist_ok=True)
    names = sorted({str(v) for row in biomes for v in row})
    outputs: list[Path] = []
    header = f"P5\n{size} {size}\n255\n".encode("ascii")
    for name in names:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        path = output_dir / f"biome_{safe}.pgm"
        payload = bytearray(
            255 if str(biomes[y][x]) == name else 0
            for y in range(size)
            for x in range(size)
        )
        path.write_bytes(header + payload)
        outputs.append(path)
    return outputs


def export_world_rasters(world: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    r16 = output_dir / "heightmap.r16"
    export_heightmap_r16(world["heightmap"], r16)
    masks = export_biome_masks_pgm(world["biomes"], output_dir / "biome_masks")
    manifest = {
        "schema_version": "1.0.0",
        "generator": world.get("generator"),
        "heightmap": r16.name,
        "heightmap_format": "R16_BE_UINT16",
        "size": len(world["heightmap"]),
        "biome_masks": [str(p.relative_to(output_dir)).replace("\\", "/") for p in masks],
    }
    (output_dir / "raster_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export NARIS world raster interchange files.")
    parser.add_argument("world_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("build/worldgen/rasters"))
    args = parser.parse_args()
    world = json.loads(args.world_json.read_text(encoding="utf-8"))
    manifest = export_world_rasters(world, args.output_dir)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
