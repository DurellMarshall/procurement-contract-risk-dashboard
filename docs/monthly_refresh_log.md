# Monthly Refresh Log

This log documents the recurring-data workflow for the Procurement & Contract Risk Dashboard.

Baseline source: recovered 2021-2025 synthetic BOCES procurement CSVs.

Generated refresh range: 2026-01 through 2026-04.

| Refresh Month | Purchase Orders | Purchase Lines | Hardware Assets | Software Entitlements | License Assignments | Contracts | Incremental Spend |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 32 | 116 | 4,259 | 39 | 17,567 | 4 | $9,032,892.37 |
| 2026-02 | 32 | 115 | 4,961 | 35 | 21,389 | 5 | $10,003,447.07 |
| 2026-03 | 32 | 126 | 4,686 | 49 | 24,849 | 7 | $9,250,912.17 |
| 2026-04 | 32 | 115 | 3,968 | 40 | 12,688 | 7 | $8,111,145.72 |

## Portfolio Talking Point

Project 2 is staged as a recurring monthly procurement reporting process. The 2021-2025 dataset acts as the historical baseline, then each monthly close generates incremental procurement, contract, license, assignment, and hardware asset records. The Power BI model can refresh against the current folder while the monthly update folders preserve the audit trail.

## Super / Notion Update Snippet

Use this wording on the Project 2 case study page after screenshots are updated:

> The dashboard uses a 2021-2025 synthetic education IT procurement baseline and a recurring monthly refresh process. January through April 2026 update packages were generated to simulate an operational reporting cadence, with purchase orders, contracts, software entitlements, license assignments, and hardware assets appended through a repeatable script.
