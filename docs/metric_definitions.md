# Metric Definitions

## Spend Metrics

**Total Spend**

Sum of `Full_Purchases_Lines[Total_Spend]` across the selected date, vendor, district, funding, and category filters.

**Hardware Spend**

Sum of `Total_Spend` where `Item_Class = Hardware`.

**Software / Subscription Spend**

Sum of `Total_Spend` where `Item_Class = License`.

**Spend Selected Range**

Total spend filtered by the active report slicers, especially date range, vendor, manufacturer, district, funding source, and category.

**Hardware Spend QTD**

Hardware spend for the current quarter-to-date period in the selected reporting calendar.

**Hardware Spend 30D**

Hardware spend for the most recent 30-day reporting period.

## Vendor And Delivery Metrics

**Units Purchased**

Sum of `Full_Purchases_Lines[Quantity]`.

**Average Delivery Days**

Average number of days between hardware purchase date and received date.

**Median Delivery Days**

Median number of days between hardware purchase date and received date.

**Delivery Status**

Text classification based on delivery speed. The current dashboard classifies the selected range as `Slight Delay`.

## Contract Metrics

**Active Contracts**

Count of contract rows where `Contract_Status = Active`.

**Active Expiring in 12M**

Count of active contracts with `Contract_End_Date` within the next 12 months of the reporting close.

**Active Expiring in 90 Days**

Count of active contracts with `Contract_End_Date` within the next 90 days of the reporting close.

**Active Expiring in 30 Days**

Count of active contracts with `Contract_End_Date` within the next 30 days of the reporting close.

**Auto-Renew Active Contracts**

Count of active contracts where `Auto_Renewal_Status = Yes`.

**Auto-Renew Expiring in 12M / 90 Days / 30 Days**

Count of active auto-renew contracts with end dates inside the stated forward-looking risk window.

## Reporting Period

The public portfolio snapshot is staged as a static April 2026 monthly close.

Main reporting calendar:

- Start: 2021-01-01
- End: 2026-04-30

Future-facing contract, warranty, and subscription end dates may extend beyond April 2026 because they represent renewal and risk exposure, not transaction activity.

