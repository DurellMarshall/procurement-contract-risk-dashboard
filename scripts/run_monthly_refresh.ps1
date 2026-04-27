param(
    [string]$StartMonth = "2026-01",
    [string]$EndMonth,
    [switch]$PreviousMonthOnly
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = "C:\Users\durel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$Script = Join-Path $PSScriptRoot "generate_monthly_refresh.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Bundled Codex Python was not found at $Python"
}

if ($PreviousMonthOnly) {
    & $Python $Script --previous-month-only
}
elseif ($EndMonth) {
    & $Python $Script --start-month $StartMonth --end-month $EndMonth
}
else {
    & $Python $Script --start-month $StartMonth
}

