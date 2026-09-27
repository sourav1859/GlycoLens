[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
$problems = @()

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
}
if ($null -eq $pythonCommand) {
    $problems += 'Python 3.10+ is not available on PATH.'
} else {
    $pythonVersion = & $pythonCommand.Source --version 2>&1
    Write-Output "Python: $pythonVersion"
}

if ($null -eq (Get-Command pipx -ErrorAction SilentlyContinue) -and $null -eq (Get-Command uv -ErrorAction SilentlyContinue)) {
    $problems += 'Neither pipx nor uv is available for isolated installation.'
}

$graphifyCommand = Get-Command graphify -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $graphifyCommand) {
    $problems += 'The graphify command is not installed.'
} else {
    Write-Output "Graphify: $(& $graphifyCommand.Source --version 2>&1)"
}

try {
    Assert-GlycoLensGraphifyExclusions -RepositoryRoot $repositoryRoot
} catch {
    $problems += $_.Exception.Message
}

if ($problems.Count -gt 0) {
    Write-Output 'Graphify readiness: BLOCKED'
    $problems | ForEach-Object { Write-Output "- $_" }
    exit 2
}

Write-Output 'Graphify readiness: PASS'
