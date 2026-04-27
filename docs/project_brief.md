# Project Brief: Procurement & Contract Risk Dashboard

## What This Project Is

This is a Power BI dashboard for an education IT procurement environment. The model connects procurement activity to districts, schools, classrooms, hardware assets, software/license records, contracts, vendors, and funding.

## Report Pages Found In The PBIX

- Finance
- Funding
- Contracts
- Vendor KPI (PO Based)

## Business Questions It Should Answer

- How much has been purchased by vendor, category, school, district, or funding source?
- Which contracts or software entitlements are approaching renewal or risk thresholds?
- Which vendors receive the most purchase order activity?
- How are purchases distributed across districts, schools, classrooms, departments, and item families?
- Where do procurement records connect to asset, license, or contract obligations?
- Are there gaps in renewal visibility, contract metadata, or assignment coverage?

## Likely Model Areas

Based on the Power BI relationship diagram and report metadata, the model appears to include:

- District and school dimensions
- Classroom dimension
- Purchase header and purchase line tables
- Contracts table
- License and license assignment tables
- Hardware asset table
- Software entitlement table
- Vendor dimension
- Date dimensions
- Risk/color helper tables and parameter tables

## Portfolio Story

This project should be framed as a procurement and contract-risk reporting project with a recurring monthly refresh workflow. It shows that Durell can work with a multi-table business model, build Power BI pages for different stakeholder needs, organize operational records into a dashboard, and maintain an update cadence that resembles a real reporting process.

## Monthly Refresh Story

The 2021-2025 source data is treated as the historical baseline. January through April 2026 refresh packages were generated using a repeatable script that creates new purchase orders, purchase lines, hardware assets, software entitlements, license assignments, and contracts based on the historical distribution of the data.

This gives the portfolio a stronger business operations story:

- baseline historical data
- monthly close/update packages
- current refresh-ready dataset
- QA checks before dashboard screenshots
- Notion/Super case study update after Power BI refresh
