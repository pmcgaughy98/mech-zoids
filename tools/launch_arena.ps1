$arenaRoot = Split-Path -Parent $PSScriptRoot
$arenaGodot = 'C:\Users\pmcga\Games\Tools\Godot_v4.7.2\Godot_v4.7.2-stable_win64.exe'
$arenaRunning = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like 'Godot_v*' }
if ($arenaRunning) {
    Write-Host 'Close the existing Godot preview or editor first. This project uses one Godot process at a time.'
    Read-Host 'Press Enter to close this launcher'
    exit 1
}
Start-Process -FilePath $arenaGodot -WorkingDirectory $arenaRoot -ArgumentList @('--path', ('"' + $arenaRoot + '"'), '--log-file', ('"' + (Join-Path $arenaRoot 'reports/arena-play.log') + '"'))
