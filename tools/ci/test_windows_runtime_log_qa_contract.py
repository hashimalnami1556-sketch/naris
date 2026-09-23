from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class WindowsRuntimeLogQAContractTests(unittest.TestCase):
    def test_package_records_smoke_start_before_launch(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        start_index = source.index("$SmokeStartedAtUtc = [DateTime]::UtcNow")
        runtime_index = source.index("[NARIS] Runtime progression + save/load smoke")
        self.assertLess(start_index, runtime_index)

    def test_package_scans_new_logs_and_crash_artifacts(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "$RuntimeEvidenceRoots",
            '"NARIS_W04\\Saved"',
            '-Filter "*.log"',
            "$SmokeStartedAtUtc",
            '$CrashRoot = Join-Path $root "Crashes"',
            "$CrashArtifacts",
        ):
            self.assertIn(token, source)

    def test_package_rejects_high_severity_runtime_failures(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            '"Fatal error:"',
            '"Unhandled Exception"',
            '"Assertion failed:"',
            '"LowLevelFatalError"',
            '"Ensure condition failed:"',
            '$RuntimeLogQaStatus -ne "pass"',
            "Runtime log/crash QA failed",
        ):
            self.assertIn(token, source)

    def test_package_writes_runtime_log_qa_evidence(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "naris.windows.runtime-log-qa.v1",
            "naris_runtime_log_qa.json",
            "runtime_log_qa_status",
            "runtime_log_qa_report",
            "runtime_log_files",
            "crash_artifacts",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
