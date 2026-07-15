[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromPipeline = $true)]
    [AllowEmptyString()]
    [string] $PipelineInput,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $QueryArguments
)

$ErrorActionPreference = 'Stop'
$queryScript = Join-Path $PSScriptRoot 'query_semantic_okf_ensemble.py'
if (-not (Test-Path -LiteralPath $queryScript -PathType Leaf)) {
    throw 'query_semantic_okf_ensemble.py is missing from the installed package'
}

if ($env:SEMANTIC_OKF_PYTHON) {
    if (-not [System.IO.Path]::IsPathFullyQualified($env:SEMANTIC_OKF_PYTHON)) {
        throw 'SEMANTIC_OKF_PYTHON must be an absolute executable path'
    }
    $python = (Resolve-Path -LiteralPath $env:SEMANTIC_OKF_PYTHON -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw 'SEMANTIC_OKF_PYTHON must resolve to a regular file'
    }
} else {
    $python = (Get-Command python -CommandType Application -ErrorAction Stop).Source
}

if ($env:SEMANTIC_OKF_HF_HUB_CACHE) {
    if (-not [System.IO.Path]::IsPathFullyQualified($env:SEMANTIC_OKF_HF_HUB_CACHE)) {
        throw 'SEMANTIC_OKF_HF_HUB_CACHE must be an absolute directory path'
    }
    $modelCache = (Resolve-Path -LiteralPath $env:SEMANTIC_OKF_HF_HUB_CACHE -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $modelCache -PathType Container)) {
        throw 'SEMANTIC_OKF_HF_HUB_CACHE must resolve to a directory'
    }
    $env:HF_HUB_CACHE = $modelCache
}
$env:HF_HUB_DISABLE_PROGRESS_BARS = '1'

if ($PSBoundParameters.ContainsKey('PipelineInput')) {
    $PipelineInput | & $python $queryScript @QueryArguments
} else {
    & $python $queryScript @QueryArguments
}
exit $LASTEXITCODE
