# verify_sha256.ps1 - verify MANIFEST.sha256 against files on disk.
# Usage: pwsh -File scripts/verify_sha256.ps1 [-Root <dir>] [-Manifest <file>]
param(
    [string]$Root = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
    [string]$Manifest = "MANIFEST.sha256"
)
$ErrorActionPreference = "Stop"
$manifestPath = Join-Path $Root $Manifest
if (-not (Test-Path $manifestPath)) { Write-Error "manifest not found: $manifestPath"; exit 2 }

$ok = 0; $bad = 0; $missing = 0
Get-Content $manifestPath -Encoding utf8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    if ($line -notmatch '^([0-9a-fA-F]{64})\s+\*?(.+)$') {
        Write-Output "FAIL malformed line: $line"; $script:bad++; return
    }
    $expected = $Matches[1].ToLower()
    $rel = $Matches[2].Trim()
    $path = Join-Path $Root ($rel -replace '/', [IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path $path)) { Write-Output "MISSING $rel"; $script:missing++; return }
    $actual = (Get-FileHash -Algorithm SHA256 -Path $path).Hash.ToLower()
    if ($actual -eq $expected) { $script:ok++ }
    else { Write-Output "FAIL $rel expected=$expected actual=$actual"; $script:bad++ }
}
Write-Output "RESULT ok=$ok bad=$bad missing=$missing"
if ($bad -gt 0 -or $missing -gt 0) { exit 1 }
exit 0
