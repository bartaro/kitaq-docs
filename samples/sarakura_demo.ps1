param([string]$Sarakura='sarakura.exe', [string]$Output=(Join-Path $PSScriptRoot 'sarakura-out'))
$ErrorActionPreference='Stop'
# These inputs are synthetic fixtures, not captured ROM behavior.
foreach ($platform in @('gb','fc')) {
    $fixture=Join-Path $PSScriptRoot ('sarakura\'+$platform)
    $dest=Join-Path $Output $platform
    & $Sarakura $platform analyze --metadata (Join-Path $fixture 'build.json') --events (Join-Path $fixture 'events.jsonl') --out $dest --fail-on never --no-repro-bundle
    if ($LASTEXITCODE -ne 0) { throw 'Analysis failed' }
    & $Sarakura validate (Join-Path $dest 'ai_diagnostics.json') --strict
    if ($LASTEXITCODE -ne 0) { throw 'Schema validation failed' }
    Write-Host ('Open '+(Join-Path $dest 'report.html'))
}
