Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$PiArguments = [string[]] $args

$requiredModel = "openai-codex/gpt-5.6-luna"
$modelIndices = @(
    for ($index = 0; $index -lt $PiArguments.Count; $index++) {
        if ($PiArguments[$index] -eq "--model") {
            $index
        }
    }
)
if ($modelIndices.Count -ne 1) {
    [Console]::Error.WriteLine("skill-arena-luna: require exactly one --model argument")
    exit 64
}
$modelIndex = $modelIndices[0]
if ($modelIndex + 1 -ge $PiArguments.Count) {
    [Console]::Error.WriteLine("skill-arena-luna: missing --model value")
    exit 64
}
if ($PiArguments[$modelIndex + 1] -ne $requiredModel) {
    [Console]::Error.WriteLine(
        "skill-arena-luna: refusing non-Luna model $($PiArguments[$modelIndex + 1])"
    )
    exit 64
}

# Invoke the PowerShell shim directly. The batch shim is constrained by cmd.exe's
# shorter command-line limit and fails for judge prompts that include a full answer.
$piCommand = (Get-Command "pi.ps1" -ErrorAction Stop).Source
$attemptTimeoutSeconds = if ($env:PI_MODEL_TIMEOUT_SECONDS) {
    [int] $env:PI_MODEL_TIMEOUT_SECONDS
} else {
    240
}
if ($attemptTimeoutSeconds -lt 1) {
    [Console]::Error.WriteLine("skill-arena-luna: invalid attempt timeout")
    exit 64
}

$attemptRoot = Join-Path ([IO.Path]::GetTempPath()) (
    "semantic-okf-pi-luna-" + [Guid]::NewGuid().ToString("N")
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
        [int] $TimeoutSeconds
    )

    $stdoutPath = Join-Path $attemptRoot "luna.stdout.txt"
    $stderrPath = Join-Path $attemptRoot "luna.stderr.txt"
    $argumentsPath = Join-Path $attemptRoot "luna.arguments.json"
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
                    "PI Luna attempt exceeded its timeout and process-tree termination " +
                    "could not be confirmed (taskkill exit $taskkillExitCode)."
                )
            }
        }
        return [pscustomobject]@{
            ExitCode = 124
            Stdout = ""
            Stderr = "PI Luna attempt timed out after $TimeoutSeconds seconds."
        }
    }

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
        ExitCode = $process.ExitCode
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
    $result = Invoke-PiAttempt -Arguments $PiArguments -TimeoutSeconds $attemptTimeoutSeconds
    if ($result.ExitCode -eq 0) {
        [Console]::Error.WriteLine("skill-arena-model=$requiredModel routing=luna-only")
        Write-CapturedStderr -Text $result.Stderr
        [Console]::Out.Write($result.Stdout)
        exit 0
    }

    [Console]::Error.WriteLine(
        "skill-arena-model=$requiredModel routing=luna-only failed=true exit=$($result.ExitCode)"
    )
    Write-CapturedStderr -Text $result.Stderr
    exit $result.ExitCode
} finally {
    Remove-Item -LiteralPath $attemptRoot -Recurse -Force -ErrorAction SilentlyContinue
}
