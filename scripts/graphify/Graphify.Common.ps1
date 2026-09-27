Set-StrictMode -Version Latest

function Get-GlycoLensRepositoryRoot {
    param([Parameter(Mandatory = $true)][string]$ScriptDirectory)

    $root = (Resolve-Path (Join-Path $ScriptDirectory '..\..')).Path
    if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
        throw "Resolved path is not the GlycoLens Git repository: $root"
    }
    return $root
}

function Get-GraphifyExecutable {
    $command = Get-Command graphify -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) {
        throw 'Graphify is unavailable. Install Python 3.10+ and pipx or uv, then install a pinned graphifyy version as documented in docs/tooling/graphify.md.'
    }
    return $command.Source
}

function Assert-GlycoLensGraphifyExclusions {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $checker = Join-Path $RepositoryRoot '.agents\skills\graphify\scripts\Test-Exclusions.ps1'
    if (-not (Test-Path -LiteralPath $checker)) {
        throw "Graphify exclusion checker is missing: $checker"
    }
    & $checker -RepositoryRoot $RepositoryRoot
}
