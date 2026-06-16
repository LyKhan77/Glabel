param(
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$DevDir = Join-Path $Root ".dev"
$Stopped = New-Object System.Collections.Generic.List[int]

function Stop-ProcessId($ProcessId) {
    if (-not $ProcessId) {
        return
    }
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $ProcessId -Force
        $Stopped.Add([int]$ProcessId)
    }
}

foreach ($name in "backend.pid", "frontend.pid") {
    $path = Join-Path $DevDir $name
    if (Test-Path $path) {
        $pidValue = (Get-Content -Path $path -Raw).Trim()
        if ($pidValue -match "^\d+$") {
            Stop-ProcessId ([int]$pidValue)
        }
        Remove-Item -LiteralPath $path -Force
    }
}

$escapedRoot = [regex]::Escape($Root)
$processes = Get-CimInstance Win32_Process | Where-Object {
    $_.ProcessId -ne $PID -and
    $_.CommandLine -match $escapedRoot -and
    $_.CommandLine -match "backend.main:app|vite"
}

foreach ($process in $processes) {
    Stop-ProcessId ([int]$process.ProcessId)
}

if (-not $Quiet) {
    if ($Stopped.Count -eq 0) {
        Write-Host "No Glabel dev server processes were running."
    } else {
        Write-Host ("Stopped Glabel dev server process IDs: " + (($Stopped | Sort-Object -Unique) -join ", "))
    }
}
