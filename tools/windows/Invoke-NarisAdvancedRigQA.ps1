param(
 [string]$Blender="C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
 [string]$BlendFile=""
)
$ErrorActionPreference="Stop"
$root=(Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$gate=Join-Path $root "tools\blender\naris_advanced_rig_weight_gate.py"
if(!(Test-Path $Blender)){ throw "Blender executable not found: $Blender" }
if([string]::IsNullOrWhiteSpace($BlendFile) -or !(Test-Path $BlendFile)){ throw "Production .blend file is required" }
& $Blender -b $BlendFile --python $gate
if($LASTEXITCODE -ne 0){ throw "Advanced Rig Blender gate failed: $LASTEXITCODE" }
$report=Join-Path (Split-Path $BlendFile) "Saved\TestReports\naris_advanced_rig_weight_gate.json"
if(!(Test-Path $report)){ throw "Rig QA report missing: $report" }
$j=Get-Content $report -Raw | ConvertFrom-Json
if(!$j.characters -or $j.characters.Count -eq 0){ throw "No skinned mesh/armature pairs audited" }
$bad=@($j.characters | Where-Object { $_.numeric_weight_gate -ne "PASS" -or !$_.structural_target_met })
if($bad.Count -gt 0){ $bad | ConvertTo-Json -Depth 8; throw "Rig structural/weight gate failed" }
Write-Host "NARIS_ADVANCED_RIG_NUMERIC_GATE_PASS"
Write-Host "Visual deformation remains PENDING_ARTIST_REVIEW by design."
