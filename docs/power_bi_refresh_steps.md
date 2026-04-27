# Power BI Refresh Steps

## Goal

Refresh Project 2 from the static April 2026 close files.

Use this folder as the Power BI source root:

`D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current`

## Why The Date Slicer May Show 2028

The dashboard has future-facing fields such as:

- `Contract_End_Date`
- `Warranty_End_Date`
- `Subscription_End_Date`

Those can correctly extend past April 2026 because they represent future risk and renewal exposure.

The report/calendar slicer should not use those future obligation dates as its main date range. The main slicer should use `Dim_Date` or `Full_Date_Dimension_2021_2026`, capped at the last full reporting month.

For the current static portfolio snapshot, the reporting calendar should end on:

`2026-04-30`

## Repoint Source Files

In Power Query Editor:

1. Select each query on the left.
2. In **Applied Steps**, click the gear icon next to **Source**.
3. Change the file path to the matching file below.
4. Keep the existing later steps such as `Promoted Headers` and `Changed Type`.

| Query | New Source File |
| --- | --- |
| `Full_Contracts` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_Contracts.csv` |
| `Full_Purchases_Lines` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_Purchases_Lines.csv` |
| `Full_Purchases_Header` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_Purchases_Header.csv` |
| `Full_License_Assignments` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_License_Assignments.csv` |
| `Full_Software_Entitlements` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_Software_Entitlements.csv` |
| `Full_Hardware_Assets` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Facts\Full_Hardware_Assets.csv` |
| `Full_Date_Dimension_2021_2026` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Full_Date_Dimension_2021_2026.csv` |
| `Full_Users` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Full_Users.csv` |
| `Full_Classrooms` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Full_Classrooms.csv` |
| `Full_Schools` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Full_Schools.csv` |
| `Full_Districts` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Full_Districts.csv` |
| `Dim_Date` | `D:\Documents\Portfolio\procurement-contract-risk-dashboard\data\current\Dimensions\Dim_Date.csv` |

## If `Dim_Date` Does Not Have A Source Gear

If `Dim_Date` is a generated query instead of a CSV source, open **Advanced Editor** and look for a hard-coded end date such as:

```powerquery
#date(2028, 12, 31)
```

Change it to:

```powerquery
#date(2026, 4, 30)
```

Better option: make `Dim_Date` reference the current date dimension:

```powerquery
let
    Source = Full_Date_Dimension_2021_2026
in
    Source
```

## After Updating Sources

1. Click **Close & Apply**.
2. Click **Refresh**.
3. Check the main date slicer.
4. It should end at **4/30/2026** for the static April 2026 snapshot.

## KPI Page Note

The Vendor KPI page currently appears less formatted than the other pages. That is a visual design cleanup, not a data refresh blocker. Reformat it after the data refresh is stable.

