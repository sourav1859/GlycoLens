[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateNotNullOrEmpty()][string]$Question
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
$graphify = Get-GraphifyExecutable -RepositoryRoot $repositoryRoot
$graphPath = Join-Path $repositoryRoot 'graphify-out\graph.json'
if (-not (Test-Path -LiteralPath $graphPath)) {
    throw 'No Graphify graph exists. Run Initialize-Graphify.ps1 after prerequisites pass.'
}

& $graphify query $Question --graph $graphPath
exit $LASTEXITCODE
