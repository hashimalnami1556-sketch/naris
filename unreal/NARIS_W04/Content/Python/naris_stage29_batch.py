"""Unattended G1 invocation. A receipt acknowledges authoring, never PIE acceptance."""
import importlib.util
import json
import os
from pathlib import Path
import unreal


def run(execute, receipt, apply=False, template=None):
    """Write a new invocation receipt even when execute raises; never reuse old data."""
    receipt = Path(receipt)
    if receipt.exists():
        raise RuntimeError('Receipt already exists; use a new invocation directory')
    result = {'schema': 'naris.stage29.invocation.v1', 'status': 'failed',
              'mode': 'apply' if apply else 'dry_run', 'G1': 'NOT_VERIFIED',
              'G2': 'NOT_RUN', 'G3': 'NOT_RUN', 'errors': []}
    try:
        report = execute(apply=apply, template=template)
        result.update(run_id=report.get('run_id'), map=report.get('map'),
                      map_saved=report.get('map_saved'), attempted=report.get('attempted'),
                      placed=report.get('placed'), errors=report.get('errors', []))
        if not result['run_id'] or result['errors']:
            raise RuntimeError('Stage29 preflight/authoring failed; inspect the engine report')
        if apply and (report.get('map_saved') is not True or report.get('attempted') != 136 or report.get('placed') != 136):
            raise RuntimeError('Incomplete authoring; no authoring success receipt issued')
        result['status'] = 'authoring_complete_requires_PIE' if apply else 'preflight_complete_requires_apply'
    except Exception as exc:
        result['errors'] = list(result['errors']) + [str(exc)]
        raise
    finally:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive create also protects against a competing/stale invocation.
        with receipt.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2)
    return result


def main():
    saved = Path(unreal.Paths.project_saved_dir()).resolve() / 'TestReports'
    receipt = Path(os.environ['NARIS_STAGE29_RECEIPT']).resolve()
    if not receipt.is_relative_to(saved):
        raise RuntimeError('Receipt must be within this project Saved/TestReports')
    mode = os.environ.get('NARIS_STAGE29_MODE', 'dry_run')
    if mode not in ('dry_run', 'apply'):
        raise RuntimeError('Unsupported Stage29 invocation mode')
    spec = importlib.util.spec_from_file_location('naris_stage29_place_batch', Path(__file__).with_name('naris_stage29_place.py'))
    placement = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(placement)
    run(placement.execute, receipt, apply=mode == 'apply', template=os.environ.get('NARIS_STAGE29_TEMPLATE') or None)


if __name__ == '__main__':
    main()
