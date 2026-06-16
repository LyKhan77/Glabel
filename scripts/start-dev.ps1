param(
    [int]$BackendPort = 8000,
    [string]$DataDir = "",
    [switch]$SkipInstall,
    [switch]$KeepExisting
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$DevDir = Join-Path $Root ".dev"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$StopScript = Join-Path $PSScriptRoot "stop-dev.ps1"
$FrontendPort = 3000

New-Item -ItemType Directory -Force -Path $DevDir | Out-Null

if (-not $KeepExisting -and (Test-Path $StopScript)) {
    & $StopScript -Quiet
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating backend virtual environment..."
    & python -m venv (Join-Path $Root ".venv")
}

if (-not $SkipInstall) {
    Write-Host "Installing backend requirements..."
    & $VenvPython -m pip install -r (Join-Path $Root "backend\requirements.txt")
}

if ([string]::IsNullOrWhiteSpace($DataDir)) {
    $DataDir = Join-Path $Root "glabel_data"
}

$BackendOut = Join-Path $DevDir "backend.out.log"
$BackendErr = Join-Path $DevDir "backend.err.log"
$FrontendOut = Join-Path $DevDir "frontend.out.log"
$FrontendErr = Join-Path $DevDir "frontend.err.log"

$BackendCommand = @"
`$env:GLABEL_DATA_DIR = '$DataDir'
& '$VenvPython' -m uvicorn backend.main:app --host 127.0.0.1 --port $BackendPort
"@

$FrontendCommand = @"
npm run dev
"@

$Backend = Start-Process `
    -FilePath "powershell" `
    -ArgumentList @("-NoProfile", "-Command", $BackendCommand) `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $BackendOut `
    -RedirectStandardError $BackendErr `
    -WindowStyle Hidden `
    -PassThru

$Frontend = Start-Process `
    -FilePath "powershell" `
    -ArgumentList @("-NoProfile", "-Command", $FrontendCommand) `
    -WorkingDirectory (Join-Path $Root "frontend") `
    -RedirectStandardOutput $FrontendOut `
    -RedirectStandardError $FrontendErr `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path (Join-Path $DevDir "backend.pid") -Value $Backend.Id -Encoding ASCII
Set-Content -Path (Join-Path $DevDir "frontend.pid") -Value $Frontend.Id -Encoding ASCII

function Wait-ForTcp($HostName, $Port, $Name) {
    for ($i = 0; $i -lt 30; $i++) {
        if ($HostName -match ":") {
            $client = [System.Net.Sockets.TcpClient]::new([System.Net.Sockets.AddressFamily]::InterNetworkV6)
        } else {
            $client = [System.Net.Sockets.TcpClient]::new()
        }
        try {
            $connect = $client.BeginConnect($HostName, $Port, $null, $null)
            if ($connect.AsyncWaitHandle.WaitOne(1000)) {
                $client.EndConnect($connect)
                Write-Host "$Name ready: ${HostName}:$Port"
                return
            }
        } catch {
        } finally {
            $client.Close()
        }
        Start-Sleep -Seconds 1
    }
    Write-Warning "$Name did not open port $Port within 30 seconds. Check logs in $DevDir."
}

Wait-ForTcp "127.0.0.1" $BackendPort "Backend"
Wait-ForTcp "::1" $FrontendPort "Frontend"

Write-Host ""
Write-Host "Glabel dev servers started."
Write-Host "Backend PID:  $($Backend.Id)"
Write-Host "Frontend PID: $($Frontend.Id)"
Write-Host "Backend:      http://127.0.0.1:$BackendPort"
Write-Host "Frontend:     http://localhost:$FrontendPort"
Write-Host "Data dir:     $DataDir"
Write-Host "Logs:         $DevDir"
Write-Host ""
Write-Host "Stop with:    .\scripts\stop-dev.ps1"
