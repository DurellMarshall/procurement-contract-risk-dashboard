param(
    [string]$TaskName = "Project2 Procurement Dashboard Monthly Refresh",
    [string]$RunTime = "08:00"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Runner = Join-Path $PSScriptRoot "run_monthly_refresh.ps1"

if (-not (Test-Path -LiteralPath $Runner)) {
    throw "Monthly refresh runner not found at $Runner"
}

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$Runner`" -PreviousMonthOnly" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At $RunTime
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Generates the previous month's Project 2 procurement dashboard refresh package." `
    -Force

Write-Host "Registered scheduled task: $TaskName"

