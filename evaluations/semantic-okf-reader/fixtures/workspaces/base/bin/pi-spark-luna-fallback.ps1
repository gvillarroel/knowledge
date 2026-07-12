Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$PiArguments = [string[]] $args

$fallbackModel = if ($env:PI_FALLBACK_MODEL) {
    $env:PI_FALLBACK_MODEL
} else {
    "openai-codex/gpt-5.6-luna"
}

$modelIndex = [Array]::IndexOf($PiArguments, "--model")
if ($modelIndex -lt 0 -or $modelIndex + 1 -ge $PiArguments.Count) {
    [Console]::Error.WriteLine("skill-arena-model-fallback: missing --model argument")
    exit 64
}

$primaryModel = $PiArguments[$modelIndex + 1]
$piCommand = (Get-Command "pi.cmd" -ErrorAction Stop).Source
$attemptTimeoutSeconds = if ($env:PI_MODEL_TIMEOUT_SECONDS) {
    [int] $env:PI_MODEL_TIMEOUT_SECONDS
} else {
    90
}
if ($attemptTimeoutSeconds -lt 1) {
    [Console]::Error.WriteLine("skill-arena-model-fallback: invalid attempt timeout")
    exit 64
}
$fallbackTimeoutSeconds = if ($env:PI_FALLBACK_TIMEOUT_SECONDS) {
    [int] $env:PI_FALLBACK_TIMEOUT_SECONDS
} else {
    $attemptTimeoutSeconds
}
if ($fallbackTimeoutSeconds -lt 1) {
    [Console]::Error.WriteLine("skill-arena-model-fallback: invalid fallback timeout")
    exit 64
}
$attemptRoot = Join-Path ([IO.Path]::GetTempPath()) (
    "semantic-okf-pi-fallback-" + [Guid]::NewGuid().ToString("N")
)
New-Item -ItemType Directory -Path $attemptRoot | Out-Null
$runnerPath = Join-Path $attemptRoot "invoke-pi-attempt.ps1"
@'
param(
    [Parameter(Mandatory = $true)] [string] $CommandPath,
    [Parameter(Mandatory = $true)] [string] $ArgumentsPath,
    [Parameter(Mandatory = $true)] [string] $StdoutPath,
    [Parameter(Mandatory = $true)] [string] $StderrPath
)
$ErrorActionPreference = "Continue"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$argumentList = [string[]] (Get-Content -LiteralPath $ArgumentsPath -Raw | ConvertFrom-Json)
& $CommandPath @argumentList 1> $StdoutPath 2> $StderrPath
exit $LASTEXITCODE
'@ | Set-Content -LiteralPath $runnerPath -Encoding UTF8

function Invoke-PiAttempt {
    param(
        [string[]] $Arguments,
        [string] $AttemptName,
        [int] $TimeoutSeconds
    )

    $stdoutPath = Join-Path $attemptRoot "$AttemptName.stdout.txt"
    $stderrPath = Join-Path $attemptRoot "$AttemptName.stderr.txt"
    $argumentsPath = Join-Path $attemptRoot "$AttemptName.arguments.json"
    $Arguments | ConvertTo-Json -Compress | Set-Content -LiteralPath $argumentsPath -Encoding UTF8
    $runnerArguments = @(
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $runnerPath,
        "-CommandPath",
        $piCommand,
        "-ArgumentsPath",
        $argumentsPath,
        "-StdoutPath",
        $stdoutPath,
        "-StderrPath",
        $stderrPath
    )
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList $runnerArguments `
        -WindowStyle Hidden -PassThru -ErrorAction Stop
    $completed = $process.WaitForExit($TimeoutSeconds * 1000)
    if (-not $completed) {
        & taskkill.exe /PID $process.Id /T /F 1> $null 2> $null
        $taskkillExitCode = $LASTEXITCODE
        $terminated = $process.WaitForExit(10000)
        if (-not $terminated) {
            return [pscustomobject]@{
                ExitCode = 125
                Stdout = ""
                Stderr = (
                    "PI attempt exceeded its timeout and process-tree termination " +
                    "could not be confirmed (taskkill exit $taskkillExitCode)."
                )
            }
        }
        return [pscustomobject]@{
            ExitCode = 124
            Stdout = ""
            Stderr = "PI attempt timed out after $TimeoutSeconds seconds."
        }
    }
    $exitCode = $process.ExitCode
    $stdout = if (Test-Path -LiteralPath $stdoutPath) {
        Get-Content -LiteralPath $stdoutPath -Raw
    } else {
        ""
    }
    $stderr = if (Test-Path -LiteralPath $stderrPath) {
        Get-Content -LiteralPath $stderrPath -Raw
    } else {
        ""
    }
    return [pscustomobject]@{
        ExitCode = $exitCode
        Stdout = $stdout
        Stderr = $stderr
    }
}

function Write-CapturedStderr {
    param([string] $Text)

    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        [Console]::Error.Write($Text)
        if (-not $Text.EndsWith("`n")) {
            [Console]::Error.WriteLine()
        }
    }
}

try {
    $primary = Invoke-PiAttempt -Arguments $PiArguments -AttemptName "primary" `
        -TimeoutSeconds $attemptTimeoutSeconds
    if ($primary.ExitCode -eq 0) {
        [Console]::Error.WriteLine(
            "skill-arena-model=$primaryModel fallback=false"
        )
        Write-CapturedStderr -Text $primary.Stderr
        [Console]::Out.Write($primary.Stdout)
        exit 0
    }

    [Console]::Error.WriteLine(
        "skill-arena-model=$primaryModel fallback-triggered=true exit=$($primary.ExitCode)"
    )
    Write-CapturedStderr -Text $primary.Stderr

    if ($fallbackModel -eq $primaryModel) {
        [Console]::Error.WriteLine(
            "skill-arena-model=$primaryModel fallback-skipped=same-model"
        )
        exit $primary.ExitCode
    }

    $fallbackArguments = [string[]] $PiArguments.Clone()
    $fallbackArguments[$modelIndex + 1] = $fallbackModel
    $fallback = Invoke-PiAttempt -Arguments $fallbackArguments -AttemptName "fallback" `
        -TimeoutSeconds $fallbackTimeoutSeconds
    if ($fallback.ExitCode -eq 0) {
        [Console]::Error.WriteLine(
            "skill-arena-model=$fallbackModel fallback=true"
        )
        Write-CapturedStderr -Text $fallback.Stderr
        [Console]::Out.Write($fallback.Stdout)
        exit 0
    }

    [Console]::Error.WriteLine(
        "skill-arena-model=$fallbackModel fallback-failed=true exit=$($fallback.ExitCode)"
    )
    Write-CapturedStderr -Text $fallback.Stderr
    exit $fallback.ExitCode
} finally {
    Remove-Item -LiteralPath $attemptRoot -Recurse -Force -ErrorAction SilentlyContinue
}
