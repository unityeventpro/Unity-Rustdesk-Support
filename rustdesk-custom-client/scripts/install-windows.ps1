$ErrorActionPreference = 'Stop'
$Installer = Join-Path $PSScriptRoot 'UnityAVSupport-Windows-Install.exe'
if (-not (Test-Path $Installer)) {
    throw "Place the branded RustDesk installer beside this script as UnityAVSupport-Windows-Install.exe"
}

$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) { throw 'Run this installer from an elevated PowerShell window.' }

$InstallProcess = Start-Process -FilePath $Installer -ArgumentList '--silent-install' -Wait -PassThru
if ($InstallProcess.ExitCode -ne 0) { throw "RustDesk installation failed with exit code $($InstallProcess.ExitCode)." }
$Candidates = @(
    (Join-Path $env:ProgramFiles 'RustDesk\RustDesk.exe'),
    (Join-Path $env:ProgramFiles 'RustDesk\rustdesk.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'RustDesk\RustDesk.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'RustDesk\rustdesk.exe')
)
$Client = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Client) { throw 'Installation finished, but the RustDesk executable was not found in Program Files.' }
if ($env:UNITY_SUPPORT_PASSWORD) {
    & $Client --password $env:UNITY_SUPPORT_PASSWORD
    if ($LASTEXITCODE -ne 0) { throw "RustDesk password configuration failed with exit code $LASTEXITCODE." }
}
Write-Host 'Unity AV Support RustDesk is installed in Program Files.' 
