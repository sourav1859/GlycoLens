[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
try {
    $graphify = Get-GraphifyExecutable -RepositoryRoot $repositoryRoot
} catch {
    Write-Output "Graphify status: BLOCKED - $($_.Exception.Message)"
    exit 2
}

Write-Output "Graphify version: $(& $graphify --version 2>&1)"
$graphPath = Join-Path $repositoryRoot 'graphify-out\graph.json'
if (-not (Test-Path -LiteralPath $graphPath)) {
    Write-Output 'Graphify status: NOT ACTIVE - graphify-out/graph.json does not exist.'
    exit 3
}

& $graphify check-update $repositoryRoot
if ($LASTEXITCODE -ne 0) {
    Write-Output 'Graphify status: STALE OR CHECK FAILED'
    exit $LASTEXITCODE
}

Write-Output 'Graphify status: ACTIVE'
