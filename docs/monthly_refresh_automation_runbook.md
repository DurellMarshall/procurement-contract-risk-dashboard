# Monthly Refresh Automation Runbook

## Goal

Project 2 should read like a recurring procurement reporting workflow, not a one-time dashboard build.

The workflow is:

1. Keep the 2021-2025 BOCES-style synthetic procurement data as the baseline.
2. Generate monthly incremental update packages.
3. Append the updates into `data/current`.
4. Refresh Power BI from `data/current`.
5. Update the Notion/Super case study with the monthly refresh note and screenshots.

## Backfill January Through April 2026

For the current portfolio launch, this is the recommended path. Treat April 2026 as the static current close.

Run this from PowerShell:

```powershell
cd "D:\Documents\Portfolio\procurement-contract-risk-dashboard"
.\scripts\run_monthly_refresh.ps1 -StartMonth "2026-01" -EndMonth "2026-04"
```

## Monthly Run After Launch

This is optional. Do not turn this on until the static April 2026 version is refreshed and screenshotted cleanly.

On the 1st of each month, generate the previous month's close:

```powershell
cd "D:\Documents\Portfolio\procurement-contract-risk-dashboard"
.\scripts\run_monthly_refresh.ps1 -PreviousMonthOnly
```

Example: running this on May 1, 2026 generates the April 2026 update package.

## Folder Outputs

- `data/monthly_updates/YYYY-MM`: incremental package for one monthly close.
- `data/current`: refresh-ready files with baseline plus all generated update rows.
- `data/monthly_refresh_summary.csv`: machine-readable refresh summary.
- `docs/monthly_refresh_log.md`: recruiter-readable refresh narrative and Super/Notion snippet.

## Power BI Refresh Setup

Point Power BI to the `data/current` files instead of the old Downloads folder.

Recommended target folder:

`D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current`

That gives the dashboard a stable source location even as the monthly generator updates the files.

## Optional Windows Task Scheduler Setup

This should only be registered after the manual refresh path works.

Helper script:

```powershell
cd "D:\Documents\Portfolio\procurement-contract-risk-dashboard"
.\scripts\register_monthly_refresh_task.ps1
```

Suggested task behavior:

- Trigger: monthly, day 1
- Time: 8:00 AM
- Action: PowerShell
- Script:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "D:\Documents\Portfolio\procurement-contract-risk-dashboard\scripts\run_monthly_refresh.ps1" -PreviousMonthOnly
```

## Super / Notion Publishing

Super does not need direct file uploads for this portfolio. The Super site reads the Notion page.

Practical workflow:

1. Run the monthly refresh.
2. Refresh Power BI.
3. Export updated screenshots.
4. Add the monthly refresh note and screenshots to the Notion Project 2 case-study page.
5. Super syncs the public page from Notion.

Fully automatic Notion updates would require a Notion API integration token and page ID. That can be added later, but the current portfolio-safe workflow is to generate the update package automatically and publish the polished narrative manually after QA.

## QA Checklist

- Confirm `docs/monthly_refresh_log.md` shows the expected month.
- Confirm `data/current/Facts/Full_Purchases_Header.csv` includes new PO dates.
- Confirm `data/current/Facts/Full_Purchases_Lines.csv` has matching `PO_ID` values.
- Confirm Power BI refreshes without missing source-file errors.
- Confirm Finance, Funding, Contracts, and Vendor KPI pages still render correctly.
- Export screenshots only after the refresh succeeds.
