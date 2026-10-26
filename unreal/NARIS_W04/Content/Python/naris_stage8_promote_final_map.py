"""Copy a structurally valid authored source to a final-map candidate.
Never renames blockout actors, replaces final assets, or treats a copy as QA approval.
"""
import json
from pathlib import Path
import unreal
from naris_shipping_map_rules import evaluate_snapshot
from naris_validate_shipping_map import collect_snapshot

FINAL = "/Game/NARIS/W04/Maps/W04_AshenForest"
BLOCKOUT = "/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"


def main():
    eal = unreal.EditorAssetLibrary
    if eal.does_asset_exist(FINAL):
        unreal.log("[NARIS] Final map already exists; leaving it untouched. Run the shipping validator separately.")
        return
    if not eal.does_asset_exist(BLOCKOUT):
        raise RuntimeError("Stage8 blocked: production blockout missing: " + BLOCKOUT)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if levels.is_in_play_in_editor() or unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("Unsaved map/PIE preserved. Save and stop before candidate creation.")
    requirements_path = Path(unreal.Paths.project_content_dir()) / "NARIS/W04/Maps/W04_ProductionMapRequirements.json"
    requirements = json.loads(requirements_path.read_text(encoding="utf-8"))
    if requirements.get('schema') != 'naris.w04.production-map-requirements.v1' or requirements.get('production_map') != FINAL:
        raise RuntimeError('Invalid canonical map promotion contract')
    if not levels.load_level(BLOCKOUT):
        raise RuntimeError("Could not inspect source map: " + BLOCKOUT)
    report = evaluate_snapshot(requirements, collect_snapshot(requirements))
    report.update(schema="naris.w04.candidate-preflight.v1", source_map=BLOCKOUT, candidate_map=FINAL, production_ready=False)
    out = Path(unreal.Paths.project_saved_dir()) / 'TestReports/naris_map_candidate_preflight.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if report['errors']:
        raise RuntimeError('Candidate blocked: replace prototype geometry and complete production actors before promotion. See ' + str(out))
    if not eal.duplicate_asset(BLOCKOUT, FINAL):
        raise RuntimeError('Could not duplicate authored source to candidate map')
    unreal.log_warning('[NARIS] Candidate copied. Structural preflight is not asset, runtime, performance or release approval.')


if __name__ == '__main__':
    main()
