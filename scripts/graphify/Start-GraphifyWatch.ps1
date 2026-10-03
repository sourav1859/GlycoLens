[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
Assert-GlycoLensGraphifyExclusions -RepositoryRoot $repositoryRoot
$graphify = Get-GraphifyExecutable -RepositoryRoot $repositoryRoot
Write-Output 'Starting Graphify code-only watch mode in the foreground. Press Ctrl+C to stop it.'
& $graphify watch $repositoryRoot
exit $LASTEXITCODE
