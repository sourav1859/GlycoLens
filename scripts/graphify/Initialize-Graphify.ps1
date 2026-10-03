[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
& (Join-Path $PSScriptRoot 'Test-GraphifyReadiness.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Assert-GlycoLensGraphifyExclusions -RepositoryRoot $repositoryRoot
$graphify = Get-GraphifyExecutable -RepositoryRoot $repositoryRoot
Write-Output 'Building a local code-only graph. Semantic document extraction is intentionally disabled.'
& $graphify extract $repositoryRoot --code-only --out $repositoryRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$graphPath = Join-Path $repositoryRoot 'graphify-out\graph.json'
& $graphify export wiki --graph $graphPath
exit $LASTEXITCODE
