[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$localConfig = Join-Path $repositoryRoot 'supabase\config.toml'

Push-Location $repositoryRoot
try {
    if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
        throw 'Supabase CLI is required.'
    }
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw 'Docker is required.'
    }
    if (-not (Test-Path -LiteralPath $localConfig)) {
        throw 'Local Supabase configuration is missing. Run supabase init; config.toml is ignored.'
    }

    $ErrorActionPreference = 'Continue'
    $startOutput = & supabase start 2>&1
    $startExitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($startExitCode -ne 0 -and $startOutput -notmatch 'already running') {
        throw 'Local Supabase failed to start. Connection output was intentionally suppressed.'
    }
    Write-Host 'Local Supabase started; generated connection details were suppressed.'

    $ErrorActionPreference = 'Continue'
    $resetOutput = & supabase db reset --local 2>&1
    $resetExitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($resetExitCode -ne 0) {
        throw 'Local database reset failed. Connection output was intentionally suppressed.'
    }
    Write-Host 'Migration and synthetic seed applied from a clean database.'

    & supabase db lint --local
    if ($LASTEXITCODE -ne 0) {
        throw 'Database lint failed.'
    }

    & supabase test db
    if ($LASTEXITCODE -ne 0) {
        throw 'Database tests failed.'
    }
}
finally {
    Pop-Location
}
