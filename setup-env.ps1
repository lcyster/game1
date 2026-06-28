param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $Root ".venv"

$RequiredPackages = @(
    "flask"
    "flask-migrate"
    "flask-sqlalchemy"
    "pillow"
    "python-dotenv"
    "requests"
    "werkzeug"
    "wikipedia"
    "pyright"
)

function Find-Python {
    $candidates = @("python3.14", "python3.13", "python3.12", "python3", "python")
    foreach ($name in $candidates) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            $version = & $command.Source --version 2>&1
            if ($version -match "Python 3\.(\d+)") {
                $minor = [int]$Matches[1]
                if ($minor -ge 11) {
                    return $command.Source
                }
            }
        }
    }
    throw "Python 3.11+ is required but not found. Install Python and add it to PATH."
}

function Ensure-Venv {
    if (-not (Test-Path (Join-Path $VenvPath "pyvenv.cfg"))) {
        Write-Host "Creating virtual environment..."
        $python = Find-Python
        & $python -m venv $VenvPath
    }
}

function Get-VenvPython {
    return Join-Path $VenvPath "Scripts\python.exe"
}

function Ensure-Packages {
    $python = Get-VenvPython
    $installed = & $python -m pip list --format=freeze 2>&1
    $missing = @()
    foreach ($package in $RequiredPackages) {
        $packageLower = $package.ToLower()
        $found = $false
        foreach ($line in $installed) {
            if ($line -match "^([^=]+)==") {
                $name = $Matches[1].ToLower()
                if ($name -eq $packageLower) {
                    $found = $true
                    break
                }
            }
        }
        if (-not $found) {
            $missing += $package
        }
    }
    if ($missing.Count -gt 0) {
        Write-Host "Installing missing packages: $($missing -join ', ')"
        & $python -m pip install --quiet $missing
    }
}

function Set-ProjectEnvironment {
    $env:FLASK_APP = "app"
    $env:VIRTUAL_ENV = $VenvPath
    $env:PATH = "$VenvPath\Scripts;$env:PATH"
}

function Import-EnvFile {
    param([string]$Path)
    if (Test-Path $Path) {
        foreach ($line in Get-Content $Path) {
            $line = $line.Trim()
            if ($line -eq "" -or $line.StartsWith("#")) { continue }
            if ($line -match "^([^=]+)=(.*)$") {
                $name = $Matches[1].Trim()
                $value = $Matches[2].Trim()
                if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                    ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}

function Main {
    Ensure-Venv
    if ($Install) {
        Ensure-Packages
        Write-Host "All packages installed."
    }
    Set-ProjectEnvironment
    Import-EnvFile (Join-Path $Root ".env")
    Import-EnvFile (Join-Path $HOME ".env.game1")
    Write-Host "Environment ready. Python: $(Get-VenvPython)"
    Write-Host "FLASK_APP=$env:FLASK_APP"
}

Main
