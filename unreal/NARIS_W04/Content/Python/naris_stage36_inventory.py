"""Read-only UE5.7 asset class inventory. Never creates or modifies assets."""
import json
from pathlib import Path
import unreal

REQUIRED = ('World', 'SkeletalMesh', 'Skeleton', 'AnimSequence', 'AnimMontage', 'AnimBlueprint', 'Material', 'Texture2D')

def audit(registry, root='/Game/NARIS'):
    records = registry.get_assets_by_path(unreal.Name(root), recursive=True)
    assets = []
    counts = {kind: 0 for kind in REQUIRED}
    for item in records:
        kind = str(item.asset_class_path.asset_name)
        assets.append({'class': kind, 'name': str(item.asset_name), 'package': str(item.package_name)})
        if kind in counts:
            counts[kind] += 1
    missing = [kind for kind in REQUIRED if counts[kind] == 0]
    return {'stage': 36, 'root': root, 'total_assets': len(assets),
            'counts': counts, 'missing_classes': missing, 'assets': assets, 'pass': not missing}

def main():
    report = audit(unreal.AssetRegistryHelpers.get_asset_registry())
    output = Path(unreal.Paths.project_saved_dir()) / 'TestReports' / 'naris_stage36_inventory.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    unreal.log('Stage36 inventory written: ' + str(output))
    if not report['pass']:
        unreal.log_warning('Stage36 missing classes: ' + ', '.join(report['missing_classes']))
    return report

if __name__ == '__main__':
    main()
