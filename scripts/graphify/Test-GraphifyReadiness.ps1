[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Graphify.Common.ps1')

$repositoryRoot = Get-GlycoLensRepositoryRoot -ScriptDirectory $PSScriptRoot
$problems = @()

$localPython = Join-Path $repositoryRoot '.cache\graphify-venv\Scripts\python.exe'
$pythonExecutable = if (Test-Path -LiteralPath $localPython) {
    $localPython
} else {
    $command = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $command) { $command.Source }
}
if ([string]::IsNullOrWhiteSpace($pythonExecutable)) {
    $command = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $command) { $pythonExecutable = $command.Source }
}
if ([string]::IsNullOrWhiteSpace($pythonExecutable)) {
    $problems += 'Python 3.10+ is not available on PATH.'
} else {
    $pythonVersion = & $pythonExecutable --version 2>&1
    Write-Output "Python: $pythonVersion"
}

if (-not (Test-Path -LiteralPath $localPython) -and $null -eq (Get-Command pipx -ErrorAction SilentlyContinue) -and $null -eq (Get-Command uv -ErrorAction SilentlyContinue)) {
    $problems += 'Neither pipx nor uv is available for isolated installation.'
}

$graphifyCommand = $null
try {
    $graphifyCommand = Get-GraphifyExecutable -RepositoryRoot $repositoryRoot
} catch {
    $problems += 'The graphify command is not installed.'
}
if ($null -ne $graphifyCommand) {
    Write-Output "Graphify: $(& $graphifyCommand --version 2>&1)"
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
