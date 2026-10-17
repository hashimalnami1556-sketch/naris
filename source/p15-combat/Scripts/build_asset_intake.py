"""Build a separate delivery from pinned uploads, preserving every original byte."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('p15_intake_sources', ROOT / 'Unreal/source_assets.py')
SOURCES = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SOURCES)


def build(inputs, output):
    inputs, output = Path(inputs), Path(output)
    records = json.loads((ROOT / 'Data/source_uploads.json').read_text(encoding='utf-8'))['files']
    payloads = {}
    for record in records:
        source = inputs / record['workspace_name']
        if not source.is_file():
            source = inputs / record['uploaded_name']
        raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Uploaded source differs: ' + record['uploaded_name'])
        payloads[record['uploaded_name']] = raw
    raw_rig = payloads['Character1_NARIS_Rigged_Prototype.glb']
    fixed_rig = SOURCES.repair_single_skin(raw_rig)
    # Refuse an ambiguous/bad archive rather than extracting arbitrary entries.
    import io
    with zipfile.ZipFile(io.BytesIO(payloads['Character 1.zip'])) as archive:
        glbs = {name for name in payloads if name.endswith('.glb')}
        if len(archive.namelist()) != len(glbs) or set(archive.namelist()) != glbs:
            raise ValueError('Source archive inventory differs from the attached GLBs')
        if any(archive.read(name) != payloads[name] for name in glbs):
            raise ValueError('Source archive contents differ from the standalone uploads')
    usd_name = 'fdb365cc-0ad2-487b.usdz'
    if not payloads[usd_name].startswith(b'PXR-USDC'):
        raise ValueError('The pinned misnamed USD source is not a USDC layer')
    # Build only a new directory; no input or prior output is overwritten.
    shutil.copytree(ROOT, output, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'Builds'))
    for folder in ('Originals', 'SourceAssets', 'CorrectedUSD'):
        (output / folder).mkdir()
    for name, payload in payloads.items():
        (output / 'Originals' / name).write_bytes(payload)
    raw_reports, active_reports = {}, {}
    for name, payload in payloads.items():
        if name.endswith('.glb'):
            raw_reports[name] = SOURCES.GLB(payload).audit()
            if name == 'Character1_NARIS_Rigged_Prototype.glb':
                name, payload = 'Character1_NARIS_Rigged_Prototype_FIXED.glb', fixed_rig
            (output / 'SourceAssets' / name).write_bytes(payload)
            active_reports[name] = SOURCES.check_source(payload)
    (output / 'CorrectedUSD' / usd_name.replace('.usdz', '.usdc')).write_bytes(payloads[usd_name])
    contract = json.loads((output / 'Data/import_spec.json').read_text())
    if set(active_reports) != set(contract['assets']) or any(
            active_reports[name]['sha256'] != contract['assets'][name]['sha256'] for name in active_reports):
        raise ValueError('Generated sources differ from the checked-in import contract')
    probe = SOURCES.GLB(raw_rig)
    next(node for node in probe.doc['nodes'] if 'mesh' in node)['skin'] = 0
    report = {'scope': 'source-intake-not-engine-acceptance', 'originals_preserved': True,
              'raw_sources': raw_reports, 'active_sources': active_reports,
              'attach_without_rebuilding_matrices': SOURCES.GLB(probe.encode()).audit(),
              'repairs': ['Attach skin 0 to the single mesh node',
                          'Recompute inverse binds as inverse(jointWorld) * meshWorld and serialize column-major'],
              'archive_glbs_identical_to_uploads': True,
              'usd': {'input': usd_name, 'detected': 'PXR-USDC', 'correction': 'extension-only byte-identical copy',
                      'semantic_validation_executed': False},
              'unreal_imported': False, 'combat_ready': False}
    (output / 'Reports/source_asset_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = build(args.inputs, args.output)
    print(json.dumps({'originals_preserved': report['originals_preserved'],
                      'active_glbs': len(report['active_sources']), 'combat_ready': False}))
