[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
)

$requiredGitIgnore = @('graphify-out/', 'data/raw/*', 'artifacts/models/*', '.env')
$requiredGraphifyIgnore = @('data/raw/', 'data/interim/', 'data/processed/', 'artifacts/', '.env')
$gitIgnorePath = Join-Path $RepositoryRoot '.gitignore'
$graphifyIgnorePath = Join-Path $RepositoryRoot '.graphifyignore'

if (-not (Test-Path -LiteralPath $gitIgnorePath) -or -not (Test-Path -LiteralPath $graphifyIgnorePath)) {
    throw 'Graphify exclusions are incomplete: .gitignore and .graphifyignore are both required.'
}

$gitIgnore = Get-Content -LiteralPath $gitIgnorePath -Raw
$graphifyIgnore = Get-Content -LiteralPath $graphifyIgnorePath -Raw
$missing = @()
foreach ($pattern in $requiredGitIgnore) {
    if (-not $gitIgnore.Contains($pattern)) { $missing += ".gitignore:$pattern" }
}
foreach ($pattern in $requiredGraphifyIgnore) {
    if (-not $graphifyIgnore.Contains($pattern)) { $missing += ".graphifyignore:$pattern" }
}

if ($missing.Count -gt 0) {
    throw "Missing Graphify exclusions: $($missing -join ', ')"
}

Write-Output 'Graphify exclusion prerequisites: PASS'
