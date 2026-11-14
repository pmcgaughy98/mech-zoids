$gorillaGodotPath = 'C:\Users\pmcga\Games\Tools\Godot_v4.7.2\Godot_v4.7.2-stable_win64.exe'
$gorillaProjectPath = 'D:\dev\new-mech-rpg'
$gorillaPreviewScript = Join-Path $PSScriptRoot 'preview.gd'
$gorillaExistingProcess = Get-Process | Where-Object { $_.ProcessName -match '^Godot.*' -and $_.ProcessName -ne 'godot-ai' }
if ($gorillaExistingProcess) {
    Write-Host 'Close the existing Godot window before opening this preview. The project uses one Godot process at a time.'
    return
}
& $gorillaGodotPath --path $gorillaProjectPath --script $gorillaPreviewScript --audio-driver Dummy -- --interactive
