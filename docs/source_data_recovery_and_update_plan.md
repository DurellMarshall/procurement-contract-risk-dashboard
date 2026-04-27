# Source Data Recovery And Update Plan

## Current Situation

The PBIX has been recovered and copied into the project folder:

`D:\Documents\Portfolio\procurement-contract-risk-dashboard\Procurement_Contract_Risk_Dashboard.pbix`

The original CSV source folder was identified from Power BI data source settings:

`C:\Users\durel\Downloads\BOCES_PowerBI_Data`

The source CSVs have been copied into the project folder:

`D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\raw`

The PBIX contains an embedded Power BI data model, so the report can open and show data. The next refresh step is to point Power BI to the copied local portfolio files instead of the Downloads folder.

## How To Check Original Source Paths In Power BI

Use these steps inside Power BI Desktop:

1. Open `Procurement_Contract_Risk_Dashboard.pbix`.
2. Go to **File > Options and settings > Data source settings**.
3. Choose **Data sources in current file**.
4. Look for any listed CSV, Excel, folder, or database paths.
5. If paths appear, copy them into this document or place the files in `data/raw/`.

## How To Check Source Logic In Power Query

1. Go to **Home > Transform data**.
2. In Power Query, click each query/table.
3. Open **Advanced Editor**.
4. Look for source lines such as:

```powerquery
Csv.Document(File.Contents("C:\path\file.csv"))
Excel.Workbook(File.Contents("C:\path\file.xlsx"))
```

5. Record the file paths and table names.
6. If the original source files still exist, copy them to:

`D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\raw`

## If The Original Files Are Gone

This is no longer the primary path because the source files were found. Keep this fallback only if a future file is missing or corrupted.

Recommended options:

- Use **DAX Studio** connected to the open PBIX and export each table with `EVALUATE 'Table Name'`.
- Use Power BI Desktop table/data view where possible to copy table data into Excel and save CSV files.
- Rebuild a fresh synthetic source dataset using the visible model design if exports are not practical.

## Tables To Recover Or Rebuild

Based on the diagram, prioritize these tables:

- Districts
- Schools
- Classrooms
- Purchases header
- Purchase lines
- Contracts
- Vendors
- Hardware assets
- Software entitlements
- Licenses
- License assignments
- Date dimension
- Risk/color helper tables

## Date-Coverage Check

After source data is recovered, check the max date in each fact table:

- Purchase order date
- Invoice date, if available
- Contract start date
- Contract end/renewal date
- Assignment date
- License start/end date
- Asset received/deployed date

Current profile result:

- Date dimension: 2021-01-01 to 2026-01-01.
- Purchase orders: 2021-01-01 to 2025-10-25.
- Hardware purchase dates: 2021-01-01 to 2025-12-31.
- Contract start dates: 2021-01-01 to 2025-12-21.
- Software entitlement start dates: 2021-01-29 to 2025-12-27.

Decision needed: keep this as a 2021-2025 historical synthetic procurement dataset, or extend facts and the date dimension into 2026 before public portfolio launch.

## QA Checks To Run

- Purchase header total should reconcile to purchase line total where both are available.
- Vendor spend totals should match purchase order totals.
- Contract counts should match visible contract dashboard totals.
- Expiring contract count should match the Contracts page.
- Funding totals should match the Funding page.
- Date filters should not hide current-period records unexpectedly.
- No slicer should create blank or unexplained KPI cards.
