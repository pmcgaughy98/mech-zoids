param([string]$Mech = 'gorilla')
$projectRoot = Split-Path -Parent $PSScriptRoot
$catalog = Get-Content -Raw -LiteralPath (Join-Path $projectRoot 'art/model_catalog/catalog.json') | ConvertFrom-Json
$entry = $catalog.entries | Where-Object { $_.id -eq $Mech } | Select-Object -First 1
if ($null -eq $entry) { throw "Unknown mech. Choose: $($catalog.entries.id -join ', ')" }
$blendPath = Join-Path $projectRoot "art/model_catalog/workspaces/$($entry.id).blend"
if (-not (Test-Path -LiteralPath $blendPath)) { throw "Workspace not built: $blendPath" }
$blenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
# This intentionally opens the requested interactive artist workspace.
Start-Process -FilePath $blenderPath -ArgumentList @(('"{0}"' -f $blendPath))
