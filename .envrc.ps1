$script:Game1ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:Game1EnvActive = $false

function Test-Game1Directory {
    $current = $PWD.Path
    return $current -eq $script:Game1ProjectPath -or $current.StartsWith("$script:Game1ProjectPath\")
}

function Enter-Game1Environment {
    if ($script:Game1EnvActive) { return }
    $script:Game1EnvActive = $true
    $setupScript = Join-Path $script:Game1ProjectPath "setup-env.ps1"
    if (Test-Path $setupScript) {
        & $setupScript -Install
    }
}

function Exit-Game1Environment {
    if (-not $script:Game1EnvActive) { return }
    $script:Game1EnvActive = $false
    if ($env:VIRTUAL_ENV) {
        $env:PATH = $env:PATH -replace [regex]::Escape("$env:VIRTUAL_ENV\Scripts;"), ""
        Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue
    }
    if ($env:FLASK_APP) {
        Remove-Item Env:\FLASK_APP -ErrorAction SilentlyContinue
    }
}

function prompt {
    if (Test-Game1Directory) {
        Enter-Game1Environment
    } else {
        Exit-Game1Environment
    }
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}
