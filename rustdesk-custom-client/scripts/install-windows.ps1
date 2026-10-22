$ErrorActionPreference = 'Stop'
if (-not $env:UNITY_SUPPORT_PASSWORD) { throw 'Set UNITY_SUPPORT_PASSWORD in this PowerShell session before installing.' }
$Installer = Join-Path $PSScriptRoot 'UnityAVSupport-RustDesk-Setup.exe'
if (-not (Test-Path $Installer)) {
    throw "Place the branded RustDesk installer beside this script as UnityAVSupport-RustDesk-Setup.exe"
}

$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) { throw 'Run this installer from an elevated PowerShell window.' }

Start-Process -FilePath $Installer -ArgumentList '--silent-install' -Wait
$Candidates = @(
    (Join-Path $env:ProgramFiles 'RustDesk\RustDesk.exe'),
    (Join-Path $env:ProgramFiles 'RustDesk\rustdesk.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'RustDesk\RustDesk.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'RustDesk\rustdesk.exe')
)
$Client = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Client) { throw 'Installation finished, but the RustDesk executable was not found in Program Files.' }
Start-Process -FilePath $Client -ArgumentList '--password',$env:UNITY_SUPPORT_PASSWORD -Wait
Write-Host 'Unity AV Support RustDesk is installed and unattended access is configured.'
