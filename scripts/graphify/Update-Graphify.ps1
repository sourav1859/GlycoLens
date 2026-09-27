[CmdletBinding()]
param(
    [switch]$IncludeDocumentation,
    [ValidateSet('gemini', 'kimi', 'claude', 'openai', 'deepseek', 'ollama')]
    [string]$Backend
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
Assert-GlycoLensGraphifyExclusions -RepositoryRoot $repositoryRoot
$graphify = Get-GraphifyExecutable

if ($IncludeDocumentation) {
    if ([string]::IsNullOrWhiteSpace($Backend)) {
        throw 'Documentation extraction requires an explicitly approved -Backend value.'
    }
    Write-Output "Documentation extraction requested with the explicitly selected backend: $Backend"
    & $graphify extract $repositoryRoot --out $repositoryRoot --backend $Backend
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $graphPath = Join-Path $repositoryRoot 'graphify-out\graph.json'
    & $graphify export wiki --graph $graphPath
} else {
    & $graphify update $repositoryRoot
    Write-Output 'Code graph update requested. Documentation semantic nodes were not explicitly refreshed; use -IncludeDocumentation only after backend approval.'
}
exit $LASTEXITCODE
