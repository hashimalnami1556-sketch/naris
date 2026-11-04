"""Fail-closed precision/source check for ENV-003 review reports, not runtime QA."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def inspect_report(rows, source_root, threshold=0.03):
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not math.isfinite(threshold) or threshold <= 0:
        raise ValueError('threshold must be finite and positive')
    if not isinstance(rows, list) or not rows:
        raise ValueError('report must contain a nonempty asset list')
    results = []
    seen = set()
    root = Path(source_root).resolve()
    for row in rows:
        errors = []
        if not isinstance(row, dict):
            raise ValueError('asset record must be an object')
        source = row.get('source')
        if not isinstance(source, str) or not source or Path(source).name != source or '\\' in source:
            errors.append('invalid source filename')
        else:
            if source in seen:
                errors.append('duplicate source')
            seen.add(source)
            path = (root / source).resolve()
            if path.parent != root or not path.is_file():
                errors.append('source missing or outside source root')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != row.get('sha256'):
                errors.append('source SHA256 mismatch')
        value = row.get('measured_concavity')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            errors.append('missing or invalid measured concavity')
        elif value > threshold:
            errors.append(f'measured concavity {value:.8f} exceeds {threshold}')
        if row.get('precision_gate') == 'FAIL':
            errors.append('upstream precision failure remains unresolved')
        results.append({'source': source, 'errors': errors})
    return {
        'precision_status': 'REJECTED' if any(r['errors'] for r in results) else 'MEASUREMENT_CHECK_ACCEPTED',
        'threshold': threshold,
        'assets': results,
        'runtime_promotion_allowed': False,
        'remaining_gates': ['physical scale', 'passage clearance', 'visual review', 'Unreal import and traversal', 'runtime performance'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--source-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inspect_report(json.loads(args.report.read_text()), args.source_root)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'precision_status': 'REJECTED', 'error': str(exc), 'runtime_promotion_allowed': False}))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['precision_status'] == 'REJECTED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
