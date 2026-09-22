"""
CALL OF NARIS — AssetForge deterministic world generator.

Standard-library only. Produces engine-neutral JSON describing:
height, biome ids, rivers, settlements, roads and streaming chunks.

The output is intended as source data for Unreal tooling rather than a
replacement for authored World Partition / Landscape assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

BIOME_FAMILIES: tuple[str, ...] = (
    "ashen",
    "frost",
    "volcanic",
    "desert",
    "swamp",
    "abyss",
    "astral",
    "canal",
    "royal",
    "forest",
    "crystal",
)

BIOME_VARIANTS: tuple[str, ...] = (
    "lowland",
    "highland",
    "ridge",
    "basin",
    "wetland",
    "scarred",
    "ruined",
    "ancient",
    "mythic",
)

BIOME_CATALOG: tuple[str, ...] = tuple(
    f"{family}_{variant}"
    for family in BIOME_FAMILIES
    for variant in BIOME_VARIANTS
)
assert len(BIOME_CATALOG) == 99


@dataclass(frozen=True)
class WorldConfig:
    seed: int = 9042026
    size: int = 256
    sea_level: float = 0.33
    chunk_size: int = 32
    settlement_count: int = 12
    river_count: int = 8
    elevation_octaves: int = 6
    climate_octaves: int = 4

    def validate(self) -> None:
        if self.size < 16:
            raise ValueError("size must be >= 16")
        if self.chunk_size < 8 or self.size % self.chunk_size != 0:
            raise ValueError("chunk_size must be >= 8 and divide size exactly")
        if not 0.0 < self.sea_level < 1.0:
            raise ValueError("sea_level must be between 0 and 1")
        if self.settlement_count < 0 or self.river_count < 0:
            raise ValueError("counts cannot be negative")


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Settlement:
    id: str
    x: int
    y: int
    tier: int
    biome: str


@dataclass(frozen=True)
class Road:
    a: str
    b: str
    points: tuple[Point, ...]


@dataclass(frozen=True)
class River:
    id: str
    points: tuple[Point, ...]


@dataclass(frozen=True)
class Chunk:
    id: str
    x0: int
    y0: int
    x1: int
    y1: int
    biome_hint: str


def _hash01(seed: int, x: int, y: int, salt: int = 0) -> float:
    payload = f"{seed}:{x}:{y}:{salt}".encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, "big") / float((1 << 64) - 1)


def _smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _value_noise(seed: int, x: float, y: float, scale: float, salt: int) -> float:
    gx = x / scale
    gy = y / scale
    x0 = math.floor(gx)
    y0 = math.floor(gy)
    x1 = x0 + 1
    y1 = y0 + 1
    tx = _smoothstep(gx - x0)
    ty = _smoothstep(gy - y0)

    a = _hash01(seed, x0, y0, salt)
    b = _hash01(seed, x1, y0, salt)
    c = _hash01(seed, x0, y1, salt)
    d = _hash01(seed, x1, y1, salt)

    return _lerp(_lerp(a, b, tx), _lerp(c, d, tx), ty)


def _fbm(seed: int, x: int, y: int, size: int, octaves: int, salt: int) -> float:
    amplitude = 1.0
    total = 0.0
    norm = 0.0
    scale = max(4.0, size / 3.0)

    for octave in range(octaves):
        total += _value_noise(seed, x, y, scale, salt + octave * 97) * amplitude
        norm += amplitude
        amplitude *= 0.5
        scale = max(2.0, scale * 0.5)
    return total / norm if norm else 0.0


def _normalize(grid: Sequence[Sequence[float]]) -> list[list[float]]:
    lo = min(min(row) for row in grid)
    hi = max(max(row) for row in grid)
    span = hi - lo or 1.0
    return [[(v - lo) / span for v in row] for row in grid]


def generate_heightmap(config: WorldConfig) -> list[list[float]]:
    """Generate island-biased FBM terrain in the range [0, 1]."""
    config.validate()
    center = (config.size - 1) / 2.0
    max_dist = math.sqrt(2.0) * center

    raw: list[list[float]] = []
    for y in range(config.size):
        row: list[float] = []
        for x in range(config.size):
            n = _fbm(
                config.seed,
                x,
                y,
                config.size,
                config.elevation_octaves,
                salt=1100,
            )
            dist = math.dist((x, y), (center, center)) / max_dist
            island = max(0.0, 1.0 - (dist ** 1.7))
            ridge = abs(2.0 * n - 1.0)
            value = 0.62 * n + 0.28 * island + 0.10 * (1.0 - ridge)
            row.append(value)
        raw.append(row)
    return _normalize(raw)


def generate_climate(config: WorldConfig) -> tuple[list[list[float]], list[list[float]]]:
    """Return moisture and temperature fields."""
    moisture: list[list[float]] = []
    temperature: list[list[float]] = []
    for y in range(config.size):
        mr: list[float] = []
        tr: list[float] = []
        latitude = abs((y / max(1, config.size - 1)) * 2.0 - 1.0)
        for x in range(config.size):
            m = _fbm(config.seed, x, y, config.size, config.climate_octaves, salt=2300)
            tnoise = _fbm(config.seed, x, y, config.size, config.climate_octaves, salt=3700)
            t = max(0.0, min(1.0, 0.68 * (1.0 - latitude) + 0.32 * tnoise))
            mr.append(m)
            tr.append(t)
        moisture.append(mr)
        temperature.append(tr)
    return moisture, temperature


def _family_index(height: float, moisture: float, temperature: float, sea_level: float) -> int:
    if height < sea_level:
        return 7
    if height > 0.86:
        return 10 if temperature > 0.48 else 1
    if temperature < 0.22:
        return 1
    if temperature > 0.78 and moisture < 0.35:
        return 3
    if temperature > 0.67 and height > 0.65:
        return 2
    if moisture > 0.78:
        return 4
    if moisture < 0.20 and height < 0.55:
        return 5
    if height > 0.74 and moisture < 0.48:
        return 6
    if 0.45 < moisture < 0.68 and 0.38 < temperature < 0.70:
        return 9
    if height > 0.60:
        return 8
    return 0


def _variant_index(height: float, moisture: float) -> int:
    if height > 0.88:
        return 2
    if height > 0.72:
        return 1
    if moisture > 0.82:
        return 4
    if height < 0.40:
        return 3
    value = height * 0.67 + moisture * 0.33
    return 5 + min(3, int(value * 4.0))


def assign_biomes(
    config: WorldConfig,
    heightmap: Sequence[Sequence[float]],
    moisture: Sequence[Sequence[float]],
    temperature: Sequence[Sequence[float]],
) -> list[list[str]]:
    grid: list[list[str]] = []
    for y in range(config.size):
        row: list[str] = []
        for x in range(config.size):
            family = _family_index(
                heightmap[y][x],
                moisture[y][x],
                temperature[y][x],
                config.sea_level,
            )
            variant = _variant_index(heightmap[y][x], moisture[y][x])
            row.append(BIOME_CATALOG[family * len(BIOME_VARIANTS) + variant])
        grid.append(row)
    return grid


_NEIGHBORS: tuple[tuple[int, int], ...] = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),            (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
)


def _downhill_path(
    heightmap: Sequence[Sequence[float]],
    start: Point,
    sea_level: float,
    max_steps: int,
) -> tuple[Point, ...]:
    size = len(heightmap)
    current = start
    seen = {(current.x, current.y)}
    points = [current]

    for _ in range(max_steps):
        if heightmap[current.y][current.x] <= sea_level:
            break

        candidates: list[tuple[float, int, int]] = []
        for dx, dy in _NEIGHBORS:
            nx = current.x + dx
            ny = current.y + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in seen:
                candidates.append((heightmap[ny][nx], nx, ny))

        if not candidates:
            break
        candidates.sort(key=lambda item: item[0])
        best_h, nx, ny = candidates[0]
        current_h = heightmap[current.y][current.x]

        if best_h > current_h + 0.015:
            break

        current = Point(nx, ny)
        seen.add((nx, ny))
        points.append(current)

    return tuple(points)


def generate_rivers(config: WorldConfig, heightmap: Sequence[Sequence[float]]) -> list[River]:
    candidates: list[tuple[float, Point]] = []
    border = max(4, config.size // 16)
    for y in range(border, config.size - border):
        for x in range(border, config.size - border):
            h = heightmap[y][x]
            if h >= 0.72:
                candidates.append((h, Point(x, y)))
    candidates.sort(key=lambda item: item[0], reverse=True)

    rivers: list[River] = []
    used_starts: list[Point] = []
    min_sep = max(8, config.size // max(3, config.river_count))

    for _, start in candidates:
        if any(math.dist((start.x, start.y), (p.x, p.y)) < min_sep for p in used_starts):
            continue
        path = _downhill_path(heightmap, start, config.sea_level, config.size * 4)
        if len(path) >= max(8, config.size // 12):
            rivers.append(River(f"R{len(rivers)+1:02d}", path))
            used_starts.append(start)
            if len(rivers) >= config.river_count:
                break
    return rivers


def generate_settlements(
    config: WorldConfig,
    heightmap: Sequence[Sequence[float]],
    biomes: Sequence[Sequence[str]],
) -> list[Settlement]:
    rng = random.Random(config.seed ^ 0xA51E)
    candidates: list[tuple[float, int, int]] = []

    for y in range(2, config.size - 2):
        for x in range(2, config.size - 2):
            h = heightmap[y][x]
            if config.sea_level + 0.05 < h < 0.77:
                local = [
                    heightmap[y + dy][x + dx]
                    for dx, dy in _NEIGHBORS
                    if 0 <= x + dx < config.size and 0 <= y + dy < config.size
                ]
                slope = max(local) - min(local)
                score = (1.0 - slope) + 0.15 * rng.random()
                candidates.append((score, x, y))

    candidates.sort(reverse=True)
    settlements: list[Settlement] = []
    min_sep = max(
        6,
        config.size // max(4, int(math.sqrt(max(1, config.settlement_count)) * 2)),
    )

    for _, x, y in candidates:
        if any(math.dist((x, y), (s.x, s.y)) < min_sep for s in settlements):
            continue
        tier = 3 if len(settlements) == 0 else (2 if len(settlements) < 4 else 1)
        settlements.append(
            Settlement(
                id=f"S{len(settlements)+1:02d}",
                x=x,
                y=y,
                tier=tier,
                biome=biomes[y][x],
            )
        )
        if len(settlements) >= config.settlement_count:
            break
    return settlements


def _line(a: Point, b: Point) -> tuple[Point, ...]:
    points: list[Point] = []
    dx = abs(b.x - a.x)
    sx = 1 if a.x < b.x else -1
    dy = -abs(b.y - a.y)
    sy = 1 if a.y < b.y else -1
    err = dx + dy
    x, y = a.x, a.y

    while True:
        points.append(Point(x, y))
        if x == b.x and y == b.y:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return tuple(points)


def generate_roads(settlements: Sequence[Settlement]) -> list[Road]:
    """Connect settlements with a deterministic minimum-spanning tree."""
    if len(settlements) < 2:
        return []

    connected = {settlements[0].id}
    by_id = {s.id: s for s in settlements}
    roads: list[Road] = []

    while len(connected) < len(settlements):
        best: tuple[float, str, str] | None = None
        for aid in sorted(connected):
            a = by_id[aid]
            for b in settlements:
                if b.id in connected:
                    continue
                d = math.dist((a.x, a.y), (b.x, b.y))
                candidate = (d, a.id, b.id)
                if best is None or candidate < best:
                    best = candidate

        if best is None:
            break
        _, aid, bid = best
        a, b = by_id[aid], by_id[bid]
        roads.append(
            Road(
                a=aid,
                b=bid,
                points=_line(Point(a.x, a.y), Point(b.x, b.y)),
            )
        )
        connected.add(bid)

    return roads


def generate_chunks(
    config: WorldConfig,
    biomes: Sequence[Sequence[str]],
) -> list[Chunk]:
    chunks: list[Chunk] = []
    c = config.chunk_size
    for y0 in range(0, config.size, c):
        for x0 in range(0, config.size, c):
            counts: dict[str, int] = {}
            for y in range(y0, y0 + c):
                for x in range(x0, x0 + c):
                    biome = biomes[y][x]
                    counts[biome] = counts.get(biome, 0) + 1
            hint = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
            chunks.append(
                Chunk(
                    id=f"C_{x0//c:02d}_{y0//c:02d}",
                    x0=x0,
                    y0=y0,
                    x1=x0 + c - 1,
                    y1=y0 + c - 1,
                    biome_hint=hint,
                )
            )
    return chunks


def _round_grid(grid: Sequence[Sequence[float]], digits: int = 5) -> list[list[float]]:
    return [[round(v, digits) for v in row] for row in grid]


def build_world(config: WorldConfig) -> dict:
    config.validate()
    heightmap = generate_heightmap(config)
    moisture, temperature = generate_climate(config)
    biomes = assign_biomes(config, heightmap, moisture, temperature)
    rivers = generate_rivers(config, heightmap)
    settlements = generate_settlements(config, heightmap, biomes)
    roads = generate_roads(settlements)
    chunks = generate_chunks(config, biomes)

    return {
        "schema_version": "1.0.0",
        "generator": "NARIS_ASSETFORGE_WORLD_GENERATOR",
        "config": asdict(config),
        "biome_catalog": list(BIOME_CATALOG),
        "heightmap": _round_grid(heightmap),
        "biomes": biomes,
        "rivers": [
            {"id": r.id, "points": [asdict(p) for p in r.points]}
            for r in rivers
        ],
        "settlements": [asdict(s) for s in settlements],
        "roads": [
            {"a": r.a, "b": r.b, "points": [asdict(p) for p in r.points]}
            for r in roads
        ],
        "chunks": [asdict(c) for c in chunks],
    }


def export_world(world: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(world, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate CALL OF NARIS engine-neutral world data."
    )
    p.add_argument("--seed", type=int, default=9042026)
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--chunk-size", type=int, default=32)
    p.add_argument("--sea-level", type=float, default=0.33)
    p.add_argument("--settlements", type=int, default=12)
    p.add_argument("--rivers", type=int, default=8)
    p.add_argument(
        "--output",
        type=Path,
        default=Path("build/worldgen/naris_world.json"),
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = WorldConfig(
        seed=args.seed,
        size=args.size,
        chunk_size=args.chunk_size,
        sea_level=args.sea_level,
        settlement_count=args.settlements,
        river_count=args.rivers,
    )
    world = build_world(config)
    export_world(world, args.output)
    print(
        f"Generated {config.size}x{config.size} world: "
        f"{len(world['settlements'])} settlements, "
        f"{len(world['rivers'])} rivers, "
        f"{len(world['chunks'])} chunks -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
