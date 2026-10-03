$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$required = @(
  "Packages/manifest.json",
  "ProjectSettings/ProjectVersion.txt",
  "ProjectSettings/EditorBuildSettings.asset",
  "Assets/NARIS/Scenes/AshGate.unity",
  "Assets/NARIS/Runtime/Naris.Runtime.asmdef",
  "Assets/NARIS/Runtime/NarisInput.cs",
  "Assets/NARIS/Runtime/PlatformProfile.cs",
  "Assets/NARIS/Runtime/PlayerMotor.cs",
  "Assets/NARIS/Runtime/WorldBootstrap.cs",
  "Assets/NARIS/Runtime/SaveStore.cs",
  "Assets/NARIS/Runtime/RuntimeSmokeTest.cs",
  "Assets/NARIS/Editor/BuildNaris.cs",
  "Assets/NARIS/Editor/NarisAssetValidation.cs",
  "Assets/NARIS/Tests/EditMode/Naris.Tests.EditMode.asmdef",
  "Assets/NARIS/Tests/EditMode/PlatformProfileTests.cs",
  "Docs/AI/PRODUCT.md",
  "Docs/AI/DESIGN.md"
)
$missing = @($required | Where-Object { -not (Test-Path (Join-Path $root $_)) })
if ($missing.Count) { throw "Missing required files: $($missing -join ', ')" }

$manifest = Get-Content (Join-Path $root "Packages/manifest.json") -Raw | ConvertFrom-Json
if (-not $manifest.dependencies.'com.unity.test-framework') { throw "Unity Test Framework package is missing" }

$player = Get-Content (Join-Path $root "Assets/NARIS/Runtime/PlayerMotor.cs") -Raw
$world = Get-Content (Join-Path $root "Assets/NARIS/Runtime/WorldBootstrap.cs") -Raw
$build = Get-Content (Join-Path $root "Assets/NARIS/Editor/BuildNaris.cs") -Raw
$tests = Get-Content (Join-Path $root "Assets/NARIS/Tests/EditMode/PlatformProfileTests.cs") -Raw
if ($player -notmatch 'NarisInput\.Read') { throw "PlayerMotor is not routed through NarisInput" }
if ($world -notmatch 'PlatformBootstrap\.ApplyCurrent') { throw "WorldBootstrap is not applying platform profile" }
foreach ($target in @('BuildWindows','BuildLinux','BuildMac','BuildWebGL')) {
  if ($build -notmatch $target) { throw "Missing build target: $target" }
}
if ($tests -notmatch 'using UnityEngine;') { throw "EditMode tests cannot resolve RuntimePlatform/Vector types" }

Write-Host "NARIS_STATIC_VERIFY_PASS required=$($required.Count) buildTargets=4"
