"""Read-only WORLD-002 R16 sampler for non-destructive NARIS landmark placement.

No Unreal dependency. Input coordinates are world metres, heights are metres.
The source 1009x1009 little-endian R16 is never rewritten.
"""
import copy
import hashlib
import math
from pathlib import Path
import struct

GRID = 1009
WORLD_EXTENT_M = 1000.0
EXPECTED_BYTES = GRID * GRID * 2


def landmark_ground_m(r16_path, x_m, y_m, expected_sha256=None):
    if not math.isfinite(x_m) or not math.isfinite(y_m) or not (-WORLD_EXTENT_M <= x_m <= WORLD_EXTENT_M and -WORLD_EXTENT_M <= y_m <= WORLD_EXTENT_M):
        raise ValueError('Landmark position outside supported 2km WORLD-002 extent')
    raw=Path(r16_path).read_bytes()
    if len(raw)!=EXPECTED_BYTES:
        raise ValueError('Expected 1009x1009 little-endian R16 bytes')
    if expected_sha256 and hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Heightmap SHA256 mismatch')
    column=round((x_m+WORLD_EXTENT_M)*(GRID-1)/(2*WORLD_EXTENT_M))
    row=round((y_m+WORLD_EXTENT_M)*(GRID-1)/(2*WORLD_EXTENT_M))
    encoded=struct.unpack_from('<H',raw,2*(row*GRID+column))[0]
    return (encoded-32768)/128.0


def corrected_landmarks(manifest, r16_path):
    output=copy.deepcopy(manifest)
    for entry in output['environment_landmarks']:
        x,y,_=entry['location_m_xyz']
        entry['location_m_xyz'][2]=landmark_ground_m(
            r16_path,x,y,output.get('source_heightmap_sha256'))
    return output
