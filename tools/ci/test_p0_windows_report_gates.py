"""Source-level failure-path checks, not CMD/PowerShell or Unreal execution."""
import pathlib,re,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
RUNNERS=('run_p0_hero_local_atomic.bat','run_p0_boss_03_local_visual.bat','run_p0_boss_04_promote_and_regress.bat','run_p0_05_promote_and_regress.bat')
class WindowsReportGates(unittest.TestCase):
 def text(self,name):return (ROOT/'tools/windows'/name).read_text()
 def test_every_jump_resolves_to_one_label(self):
  for name in RUNNERS:
   text=self.text(name);labels=re.findall(r'^:([\w]+)\s*$',text,re.M)
   self.assertEqual(len(labels),len(set(labels)),name)
   for target in re.findall(r'\bgoto\s+:([\w]+)',text,re.I):self.assertIn(target,labels,name+': '+target)
 def test_json_writers_are_compatible_with_windows_powershell(self):
  for name in RUNNERS:
   text=self.text(name)
   self.assertNotIn('-Encoding utf8NoBOM',text)
   self.assertIn('[System.Text.UTF8Encoding]::new($false)',text)
   for command in text.split('-Command ^\n')[1:]:self.assertTrue(command.startswith(' "$ErrorActionPreference=\'Stop\';" ^'),name)
 def test_acceptance_write_failure_cannot_print_success(self):
  hero=self.text(RUNNERS[3]);boss=self.text(RUNNERS[2])
  self.assertRegex(hero,r"WriteAllText\('%REPORT%',\(\$o\|ConvertTo-Json -Depth 6\).*\nif errorlevel 1 goto :rollback_report")
  self.assertIn('acceptance_report_write_failed',boss)
  for text,token in ((hero,'[P0-05] PASS -'),(boss,'[ASH-WARDEN-04] PASS -')):
   write=text.index('[System.IO.File]::WriteAllText(');success=text.index(token)
   self.assertIn('if errorlevel 1',text[write:success])
 def test_promotion_and_rollback_require_fresh_success_reports(self):
  text=self.text(RUNNERS[3])
  self.assertIn('for %%F in ("%REPORT%" "%PROMOTION_REPORT%")',text)
  self.assertIn("$p.status -ne 'PASS' -or $p.promoted -ne $true",text)
  self.assertIn('if exist "%ROLLBACK_REPORT%" del /q "%ROLLBACK_REPORT%"',text)
  self.assertIn("$r.rolled_back -ne $true -or $r.active_preserved -ne $true",text)
if __name__=='__main__':unittest.main()
