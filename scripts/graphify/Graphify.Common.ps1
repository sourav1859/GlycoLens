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
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    if (-not [string]::IsNullOrWhiteSpace($env:GLYCOLENS_GRAPHIFY_EXECUTABLE)) {
        $configured = [System.IO.Path]::GetFullPath($env:GLYCOLENS_GRAPHIFY_EXECUTABLE)
        if (-not (Test-Path -LiteralPath $configured)) {
            throw "GLYCOLENS_GRAPHIFY_EXECUTABLE does not exist: $configured"
        }
        return $configured
    }

    $localExecutable = Join-Path $RepositoryRoot '.cache\graphify-venv\Scripts\graphify.exe'
    if (Test-Path -LiteralPath $localExecutable) {
        return $localExecutable
    }

    $command = Get-Command graphify -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) {
        throw 'Graphify is unavailable. Install Python 3.10+ and the pinned graphifyy version as documented in docs/tooling/graphify.md.'
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
