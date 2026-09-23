from pathlib import Path
import tempfile
import unittest
from validate_unreal_source import validate_source


class UnrealSourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'NARIS_W04.Target.cs').write_text('public class NARIS_W04Target : TargetRules {}')
        (self.root / 'NARIS_W04Editor.Target.cs').write_text('public class NARIS_W04EditorTarget : TargetRules {}')
        (self.root / 'Module.cpp').write_text('IMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, NARIS_W04, "NARIS_W04");')

    def test_valid_bootstrap(self):
        self.assertEqual([], validate_source(self.root))

    def test_duplicate_target_and_module_are_detected(self):
        (self.root / 'Duplicate.Target.cs').write_text('public class NARIS_W04Target : TargetRules {}')
        (self.root / 'Other.cpp').write_text('IMPLEMENT_MODULE(FDefaultModuleImpl, NARIS_W04)')
        errors = validate_source(self.root)
        self.assertTrue(any('NARIS_W04Target' in e and 'found 2' in e for e in errors))
        self.assertTrue(any('module registration' in e and 'found 2' in e for e in errors))

    def test_empty_file_and_missing_editor_are_detected(self):
        (self.root / 'NARIS_W04Editor.Target.cs').unlink()
        (self.root / 'Empty.h').write_text('')
        errors = validate_source(self.root)
        self.assertTrue(any('Empty Unreal source' in e for e in errors))
        self.assertTrue(any('NARIS_W04EditorTarget' in e and 'found 0' in e for e in errors))

    def test_comments_are_not_registrations(self):
        (self.root / 'Comment.cpp').write_text('// IMPLEMENT_MODULE(FDefaultModuleImpl, NARIS_W04)\n/* IMPLEMENT_MODULE(FDefaultModuleImpl, NARIS_W04) */')
        self.assertEqual([], validate_source(self.root))

    def test_duplicate_reflected_enum_is_detected(self):
        enum_text = 'UENUM(BlueprintType) enum class ENarisBossPhase : uint8 { P1, P2 };'
        (self.root / 'BossA.h').write_text(enum_text)
        (self.root / 'BossB.h').write_text(enum_text)
        errors = validate_source(self.root)
        self.assertTrue(any('Duplicate reflected enum ENarisBossPhase' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
