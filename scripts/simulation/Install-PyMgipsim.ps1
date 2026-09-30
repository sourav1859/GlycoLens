[CmdletBinding()]
param(
    [string]$SourceDirectory = ".cache/pymgipsim-source",
    [string]$EnvironmentDirectory = ".cache/pymgipsim-venv"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$sourcePath = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $SourceDirectory))
$environmentPath = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $EnvironmentDirectory))
$lockPath = Join-Path $repositoryRoot "research/simulation/pymgipsim-requirements.lock"
$upstreamUrl = "https://github.com/illinoistech-itm/py-mgipsim.git"
$upstreamCommit = "b985f8c2ea385d1b2b8480957b730866e07772f1"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is required to install the pinned py-mgipsim source."
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required to create the isolated py-mgipsim environment."
}

if (-not (Test-Path -LiteralPath $sourcePath)) {
    & git clone --filter=blob:none $upstreamUrl $sourcePath
    if ($LASTEXITCODE -ne 0) { throw "Unable to clone py-mgipsim." }
    & git -C $sourcePath checkout --detach $upstreamCommit
    if ($LASTEXITCODE -ne 0) { throw "Unable to check out the reviewed py-mgipsim commit." }
}

$actualCommit = (& git -c "safe.directory=$($sourcePath.Replace('\', '/'))" -C $sourcePath rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualCommit -ne $upstreamCommit) {
    throw "The existing py-mgipsim checkout is not at the reviewed commit. Remove only the dedicated ignored cache directory and rerun this script."
}

$pythonPath = Join-Path $environmentPath "Scripts/python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) {
    & uv venv $environmentPath --python 3.12
    if ($LASTEXITCODE -ne 0) { throw "Unable to create the isolated py-mgipsim environment." }
}

& uv pip sync --python $pythonPath $lockPath
if ($LASTEXITCODE -ne 0) { throw "Unable to synchronize the pinned py-mgipsim dependencies." }

Write-Output "Pinned py-mgipsim source and isolated dependencies are ready."
Write-Output "Run: uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution"
