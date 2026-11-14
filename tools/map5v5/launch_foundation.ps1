$ErrorActionPreference = 'Stop'
$projectPath = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runningGodot = Get-Process | Where-Object { $_.ProcessName -match '^Godot_v' }
if ($runningGodot) {
    Write-Host 'A Godot app is already running. Close that preview yourself before launching the foundation.'
    exit 1
}
& 'C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64_console.exe' --path $projectPath 'res://scenes/map5v5/foundation.tscn'
