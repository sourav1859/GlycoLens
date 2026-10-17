[CmdletBinding()]
param()

# Captures local CLI values privately; no credentials/connection details reach stdout.
$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $repositoryRoot
try {
    $ErrorActionPreference = 'Continue'
    $rawStatus = & supabase status -o json 2>$null
    $statusExitCode = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($statusExitCode -ne 0) { throw 'Start local Supabase before configuring the demo.' }
    $localStatus = ($rawStatus -join "`n") | ConvertFrom-Json
    if (-not $localStatus.API_URL -or -not $localStatus.ANON_KEY -or -not $localStatus.SERVICE_ROLE_KEY) {
        throw 'Local Supabase status is missing required values.'
    }
    $environmentPath = Join-Path $repositoryRoot '.env'
    $existing = if (Test-Path -LiteralPath $environmentPath) { Get-Content -LiteralPath $environmentPath } else { @() }
    $kept = @($existing | Where-Object { $_ -notmatch '^SUPABASE_(URL|ANON_KEY|SERVICE_ROLE_KEY)=' })
    $kept += 'SUPABASE_URL=' + $localStatus.API_URL
    $kept += 'SUPABASE_ANON_KEY=' + $localStatus.ANON_KEY
    $kept += 'SUPABASE_SERVICE_ROLE_KEY=' + $localStatus.SERVICE_ROLE_KEY
    if (-not ($kept -match '^OPEN_FOOD_FACTS_USER_AGENT=')) { $kept += 'OPEN_FOOD_FACTS_USER_AGENT=GlycoLens/0.1' }
    [IO.File]::WriteAllLines($environmentPath, [string[]]$kept, [Text.UTF8Encoding]::new($false))
    $clientPath = Join-Path $repositoryRoot 'frontend/.env.local'
    $clientExisting = if (Test-Path -LiteralPath $clientPath) { Get-Content -LiteralPath $clientPath } else { @() }
    $clientKept = @($clientExisting | Where-Object { $_ -notmatch '^NEXT_PUBLIC_SUPABASE_(URL|ANON_KEY)=' })
    $clientKept += 'NEXT_PUBLIC_SUPABASE_URL=' + $localStatus.API_URL
    $clientKept += 'NEXT_PUBLIC_SUPABASE_ANON_KEY=' + $localStatus.ANON_KEY
    [IO.File]::WriteAllLines($clientPath, [string[]]$clientKept, [Text.UTF8Encoding]::new($false))
    $configPath = Join-Path $repositoryRoot 'supabase/config.toml'
    $configText = [IO.File]::ReadAllText($configPath)
    if ($configText -match 'enable_anonymous_sign_ins\s*=') {
        $configText = $configText -replace 'enable_anonymous_sign_ins\s*=\s*false', 'enable_anonymous_sign_ins = true'
    } else {
        $configText = $configText -replace '(?m)^\[auth\]\s*$', "[auth]`nenable_anonymous_sign_ins = true"
    }
    [IO.File]::WriteAllText($configPath, $configText, [Text.UTF8Encoding]::new($false))
    Write-Output 'Ignored local server/client configuration written. Restart local Supabase to apply demo Auth settings.'
} finally { Pop-Location }
