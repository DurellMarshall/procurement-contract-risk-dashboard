"""
Generate recurring monthly refresh files for the Procurement & Contract Risk Dashboard.

The recovered 2021-2025 source data stays in data/raw. This script creates:
- data/monthly_updates/YYYY-MM: incremental rows generated for each monthly close
- data/current: current refresh-ready files with baseline plus all generated updates
- docs/monthly_refresh_log.md: human-readable refresh history for portfolio/Notion/Super
"""

from __future__ import annotations

import argparse
import calendar
import random
import string
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
MONTHLY = PROJECT_ROOT / "data" / "monthly_updates"
CURRENT = PROJECT_ROOT / "data" / "current"
DOCS = PROJECT_ROOT / "docs"


FACT_FILES = {
    "contracts": RAW / "Facts" / "Full_Contracts.csv",
    "hardware": RAW / "Facts" / "Full_Hardware_Assets.csv",
    "assignments": RAW / "Facts" / "Full_License_Assignments.csv",
    "purchase_header": RAW / "Facts" / "Full_Purchases_Header.csv",
    "purchase_lines": RAW / "Facts" / "Full_Purchases_Lines.csv",
    "software": RAW / "Facts" / "Full_Software_Entitlements.csv",
}

DIM_FILES = {
    "classrooms": RAW / "Dimensions" / "Full_Classrooms.csv",
    "date": RAW / "Dimensions" / "Full_Date_Dimension_2021_2026.csv",
    "districts": RAW / "Dimensions" / "Full_Districts.csv",
    "schools": RAW / "Dimensions" / "Full_Schools.csv",
    "users": RAW / "Dimensions" / "Full_Users.csv",
}


@dataclass
class IdState:
    next_contract_id: int
    next_asset_id: int
    next_assignment_id: int
    next_license_id: int
    next_po_id: int
    used_po_numbers: set[str]
    used_asset_tags: set[str]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def parse_month(value: str) -> date:
    return datetime.strptime(value, "%Y-%m").date().replace(day=1)


def month_iter(start_month: str, end_month: str) -> list[date]:
    start = parse_month(start_month)
    end = parse_month(end_month)
    months = []
    cur = start
    while cur <= end:
        months.append(cur)
        year = cur.year + (1 if cur.month == 12 else 0)
        month = 1 if cur.month == 12 else cur.month + 1
        cur = date(year, month, 1)
    return months


def month_end(month: date) -> date:
    return date(month.year, month.month, calendar.monthrange(month.year, month.month)[1])


def add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, max_day))


def add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(month=2, day=28, year=day.year + years)


def fmt(day: date) -> str:
    return day.isoformat()


def to_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: float) -> str:
    return f"{value:.2f}"


def numeric_tail(series: pd.Series, prefix: str = "") -> int:
    tails = []
    for value in series.astype(str):
        cleaned = value.replace(prefix, "") if prefix else value
        digits = "".join(ch for ch in cleaned if ch.isdigit())
        if digits:
            tails.append(int(digits))
    return max(tails) if tails else 0


def random_day(rng: random.Random, month: date) -> date:
    return date(month.year, month.month, rng.randint(1, calendar.monthrange(month.year, month.month)[1]))


def random_serial(rng: random.Random, length: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(rng.choice(alphabet) for _ in range(length))


def fiscal_month(month_number: int) -> int:
    return ((month_number - 7) % 12) + 1


def fiscal_year(day: date) -> int:
    return day.year + 1 if day.month >= 7 else day.year


def build_date_dimension(end_day: date) -> pd.DataFrame:
    rows = []
    cur = date(2021, 1, 1)
    while cur <= end_day:
        rows.append(
            {
                "Date": fmt(cur),
                "Year": str(cur.year),
                "Month": str(cur.month),
                "MonthName": cur.strftime("%b"),
                "Quarter": str((cur.month - 1) // 3 + 1),
                "YearMonth": f"{cur.year}-{cur.month:02d}",
                "FiscalYear": str(fiscal_year(cur)),
                "FiscalMonth": str(fiscal_month(cur.month)),
            }
        )
        cur += timedelta(days=1)
    return pd.DataFrame(rows)


def initialize_state(facts: dict[str, pd.DataFrame]) -> IdState:
    return IdState(
        next_contract_id=numeric_tail(facts["contracts"]["Contract_ID"], "CT-") + 1,
        next_asset_id=numeric_tail(facts["hardware"]["Asset_ID"]) + 1,
        next_assignment_id=numeric_tail(facts["assignments"]["Assignment_ID"]) + 1,
        next_license_id=numeric_tail(facts["software"]["License_ID"]) + 1,
        next_po_id=numeric_tail(facts["purchase_header"]["PO_ID"]) + 1,
        used_po_numbers=set(facts["purchase_header"]["PO_Number"].astype(str)),
        used_asset_tags=set(facts["hardware"]["Asset_Tag"].astype(str)),
    )


def next_po_number(state: IdState, rng: random.Random) -> str:
    while True:
        value = f"PO-{rng.randint(100000, 999999)}"
        if value not in state.used_po_numbers:
            state.used_po_numbers.add(value)
            return value


def next_asset_tag(state: IdState, rng: random.Random) -> str:
    while True:
        value = str(rng.randint(10000000, 99999999))
        if value not in state.used_asset_tags:
            state.used_asset_tags.add(value)
            return value


def sample_users(users: pd.DataFrame, district_id: str, school_id: str, count: int, rng: random.Random) -> pd.DataFrame:
    subset = users[(users["District_ID"] == district_id) & (users["School_ID"] == school_id)]
    if subset.empty:
        subset = users[users["District_ID"] == district_id]
    if subset.empty:
        subset = users
    if subset.empty:
        return subset
    replace = count > len(subset)
    return subset.sample(n=count, replace=replace, random_state=rng.randint(1, 999_999))


def generate_contracts(month: date, facts: dict[str, pd.DataFrame], state: IdState, rng: random.Random) -> pd.DataFrame:
    source = facts["contracts"].copy()
    source["_start"] = pd.to_datetime(source["Contract_Start_Date"], errors="coerce")
    same_month = source[(source["_start"].dt.year == 2025) & (source["_start"].dt.month == month.month)]
    pool = same_month if not same_month.empty else source[source["_start"].dt.year == 2025]
    n = max(4, min(9, len(pool))) if len(pool) else 4
    sample = pool.sample(n=n, replace=len(pool) < n, random_state=rng.randint(1, 999_999)).drop(columns=["_start"])

    rows = []
    for _, row in sample.iterrows():
        start = random_day(rng, month)
        term_years = rng.choice([1, 2, 3, 4, 5])
        end = add_years(start, term_years) - timedelta(days=rng.randint(0, 20))
        new = row.to_dict()
        new["Contract_ID"] = f"CT-{state.next_contract_id}"
        state.next_contract_id += 1
        new["Contract_Start_Date"] = fmt(start)
        new["Contract_End_Date"] = fmt(end)
        new["Contract_Status"] = "Active"
        rows.append(new)
    return pd.DataFrame(rows, columns=facts["contracts"].columns)


def generate_purchases(
    month: date,
    facts: dict[str, pd.DataFrame],
    state: IdState,
    rng: random.Random,
    new_contracts: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    headers = facts["purchase_header"].copy()
    headers["_date"] = pd.to_datetime(headers["PO_Date"], errors="coerce")
    recent = headers[headers["_date"].dt.year == 2025]
    pool = recent if not recent.empty else headers
    n_headers = 32
    sampled_headers = pool.sample(n=n_headers, replace=len(pool) < n_headers, random_state=rng.randint(1, 999_999))

    lines = facts["purchase_lines"]
    new_headers = []
    new_lines = []
    po_date_by_id = {}
    contract_ids = new_contracts["Contract_ID"].astype(str).tolist() if not new_contracts.empty else []

    for _, header in sampled_headers.iterrows():
        old_po_id = header["PO_ID"]
        new_po_id = str(state.next_po_id)
        state.next_po_id += 1
        po_date = random_day(rng, month)
        po_date_by_id[new_po_id] = po_date

        new_header = header.drop(labels=["_date"]).to_dict()
        new_header["PO_ID"] = new_po_id
        new_header["PO_Number"] = next_po_number(state, rng)
        new_header["PO_Date"] = fmt(po_date)
        new_headers.append(new_header)

        old_lines = lines[lines["PO_ID"] == old_po_id]
        if old_lines.empty:
            old_lines = lines.sample(n=1, random_state=rng.randint(1, 999_999))

        for _, line in old_lines.iterrows():
            qty = max(1, int(round(to_float(line.get("Quantity", "1"), 1) * rng.uniform(0.88, 1.14))))
            msrp = max(1.0, to_float(line.get("Unit_MSRP", "1"), 1) * rng.uniform(0.98, 1.05))
            negotiated = min(msrp, max(1.0, to_float(line.get("Unit_Negotiated", "1"), 1) * rng.uniform(0.97, 1.04)))
            total_spend = qty * negotiated
            total_savings = max(0.0, qty * (msrp - negotiated))

            new_line = line.to_dict()
            new_line["PO_ID"] = new_po_id
            new_line["Quantity"] = str(qty)
            new_line["Unit_MSRP"] = money(msrp)
            new_line["Unit_Negotiated"] = money(negotiated)
            new_line["Total_Spend"] = money(total_spend)
            new_line["Total_Savings"] = money(total_savings)

            warranty_years = to_int(new_line.get("Warranty_Years", ""), 0)
            if warranty_years:
                new_line["Warranty_End_Date_Line"] = fmt(add_years(po_date, warranty_years))

            term_months = to_int(new_line.get("Term_Months", ""), 0)
            if term_months:
                new_line["Subscription_End_Date"] = fmt(add_months(po_date, term_months))

            if contract_ids and rng.random() < 0.35:
                new_line["Contract_ID"] = rng.choice(contract_ids)
            new_lines.append(new_line)

    return (
        pd.DataFrame(new_headers, columns=facts["purchase_header"].columns),
        pd.DataFrame(new_lines, columns=facts["purchase_lines"].columns),
    )


def generate_hardware_assets(
    purchase_headers: pd.DataFrame,
    purchase_lines: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
    facts: dict[str, pd.DataFrame],
    state: IdState,
    rng: random.Random,
) -> pd.DataFrame:
    header_dates = dict(zip(purchase_headers["PO_ID"], purchase_headers["PO_Date"]))
    hardware_lines = purchase_lines[purchase_lines["Item_Class"] == "Hardware"]
    if hardware_lines.empty:
        return pd.DataFrame(columns=facts["hardware"].columns)

    classrooms = dims["classrooms"]
    users = dims["users"]
    rows = []
    status_choices = ["Deployed", "In Storage", "Pending Deployment"]
    status_weights = [0.84, 0.10, 0.06]
    condition_choices = ["Good", "Fair", "Poor"]
    condition_weights = [0.82, 0.15, 0.03]

    for _, line in hardware_lines.iterrows():
        quantity = to_int(line["Quantity"], 1)
        po_date = datetime.strptime(header_dates[line["PO_ID"]], "%Y-%m-%d").date()
        asset_count = max(1, min(quantity, 180))
        school_id = line["School_ID"]
        district_id = line["District_ID"]
        user_sample = sample_users(users, district_id, school_id, asset_count, rng)
        room_pool = classrooms[classrooms["School_ID"] == school_id]

        for i in range(asset_count):
            received = po_date + timedelta(days=rng.randint(3, 25))
            warranty_years = max(1, to_int(line.get("Warranty_Years", ""), rng.choice([3, 4, 5])))
            warranty_end = add_years(po_date, warranty_years)
            user_name = ""
            if not user_sample.empty and rng.random() < 0.88:
                user_name = user_sample.iloc[i % len(user_sample)]["Full_Name"]
            location = ""
            if not room_pool.empty:
                location = room_pool.sample(n=1, random_state=rng.randint(1, 999_999)).iloc[0]["Room"]

            rows.append(
                {
                    "Asset_ID": str(state.next_asset_id),
                    "Asset_Tag": next_asset_tag(state, rng),
                    "Item_Class": "Hardware",
                    "Item_Family": line["Item_Family"],
                    "Asset_Type": line["ItemType"],
                    "Manufacturer": line["Manufacturer"],
                    "Model": line["Item_Family_Name"],
                    "Serial_Number": random_serial(rng),
                    "Purchase_Date": fmt(po_date),
                    "Date_Received": fmt(received),
                    "Warranty_Years": str(warranty_years),
                    "Warranty_End_Date": fmt(warranty_end),
                    "Expected_Replacement_Year": str(warranty_end.year),
                    "Asset_Status": rng.choices(status_choices, status_weights)[0],
                    "Asset_Condition": rng.choices(condition_choices, condition_weights)[0],
                    "Assigned_User": user_name,
                    "Department_Owner": rng.choice(["District IT", "School IT"]),
                    "School_ID": school_id,
                    "School_Name": line["School_Name"],
                    "District_ID": district_id,
                    "District_Name": line["District_Name"],
                    "BOCES_Region": line["BOCES_Region"],
                    "Location_Detail": location,
                }
            )
            state.next_asset_id += 1

    return pd.DataFrame(rows, columns=facts["hardware"].columns)


def generate_software_and_assignments(
    purchase_headers: pd.DataFrame,
    purchase_lines: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
    facts: dict[str, pd.DataFrame],
    state: IdState,
    rng: random.Random,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    header_dates = dict(zip(purchase_headers["PO_ID"], purchase_headers["PO_Date"]))
    license_lines = purchase_lines[purchase_lines["Item_Class"] == "License"]
    if license_lines.empty:
        return pd.DataFrame(columns=facts["software"].columns), pd.DataFrame(columns=facts["assignments"].columns)

    users = dims["users"]
    software_rows = []
    assignment_rows = []

    for _, line in license_lines.iterrows():
        po_date = datetime.strptime(header_dates[line["PO_ID"]], "%Y-%m-%d").date()
        term_months = max(12, to_int(line.get("Term_Months", ""), 12))
        license_id = str(state.next_license_id)
        state.next_license_id += 1
        quantity = max(1, to_int(line.get("Quantity", ""), 1))
        license_type = rng.choice(["User-based", "Device-based", "Site-based"])
        department = rng.choice(["District IT", "School IT", "IT / Security"])

        software_rows.append(
            {
                "License_ID": license_id,
                "Item_Class": "License",
                "Item_Family": line["Item_Family"],
                "Software_Name": line["ItemType"],
                "Manufacturer": line["Manufacturer"],
                "License_Type": license_type,
                "SKU": line["Item_Family_Name"],
                "Term_Months": str(term_months),
                "Subscription_Start_Date": fmt(po_date),
                "Subscription_End_Date": fmt(add_months(po_date, term_months)),
                "Auto_Renewal_Status": rng.choice(["Yes", "No"]),
                "License_Status": "Active",
                "Quantity_Purchased": str(quantity),
                "Unit_Cost": money(to_float(line.get("Unit_Negotiated", ""), 0)),
                "Total_Cost": money(to_float(line.get("Total_Spend", ""), 0)),
                "Department_Owner": department,
                "District_ID": line["District_ID"],
                "District_Name": line["District_Name"],
                "BOCES_Region": line["BOCES_Region"],
            }
        )

        assign_count = min(quantity, 1200)
        selected_users = sample_users(users, line["District_ID"], line["School_ID"], assign_count, rng)
        for i in range(assign_count):
            if selected_users.empty:
                break
            user = selected_users.iloc[i % len(selected_users)]
            assignment_start = po_date + timedelta(days=rng.randint(0, 21))
            assignment_end = add_months(assignment_start, term_months)
            assignment_rows.append(
                {
                    "Assignment_ID": str(state.next_assignment_id),
                    "License_ID": license_id,
                    "Assignee_Type": "User",
                    "User_ID": user["User_ID"],
                    "Asset_ID": "",
                    "Assignment_Start_Date": fmt(assignment_start),
                    "Assignment_End_Date": fmt(assignment_end),
                    "Assignment_Status": "Active",
                    "District_ID": line["District_ID"],
                    "School_ID": line["School_ID"],
                }
            )
            state.next_assignment_id += 1

    return (
        pd.DataFrame(software_rows, columns=facts["software"].columns),
        pd.DataFrame(assignment_rows, columns=facts["assignments"].columns),
    )


def write_month_package(
    month: date,
    dims: dict[str, pd.DataFrame],
    facts: dict[str, pd.DataFrame],
    increments: dict[str, pd.DataFrame],
) -> None:
    month_dir = MONTHLY / f"{month.year}-{month.month:02d}"
    facts_dir = month_dir / "Facts"
    dims_dir = month_dir / "Dimensions"

    write_csv(increments["contracts"], facts_dir / "Full_Contracts.csv")
    write_csv(increments["hardware"], facts_dir / "Full_Hardware_Assets.csv")
    write_csv(increments["assignments"], facts_dir / "Full_License_Assignments.csv")
    write_csv(increments["purchase_header"], facts_dir / "Full_Purchases_Header.csv")
    write_csv(increments["purchase_lines"], facts_dir / "Full_Purchases_Lines.csv")
    write_csv(increments["software"], facts_dir / "Full_Software_Entitlements.csv")

    date_month = build_date_dimension(month_end(month))
    date_month = date_month[date_month["YearMonth"] == f"{month.year}-{month.month:02d}"]
    write_csv(date_month, dims_dir / "Full_Date_Dimension_Month.csv")

    summary_rows = [
        {"table": "Full_Contracts", "rows_added": len(increments["contracts"])},
        {"table": "Full_Hardware_Assets", "rows_added": len(increments["hardware"])},
        {"table": "Full_License_Assignments", "rows_added": len(increments["assignments"])},
        {"table": "Full_Purchases_Header", "rows_added": len(increments["purchase_header"])},
        {"table": "Full_Purchases_Lines", "rows_added": len(increments["purchase_lines"])},
        {"table": "Full_Software_Entitlements", "rows_added": len(increments["software"])},
    ]
    write_csv(pd.DataFrame(summary_rows), month_dir / "refresh_summary.csv")


def write_current(dims: dict[str, pd.DataFrame], facts: dict[str, pd.DataFrame], end_month: date) -> None:
    current_date_dimension = build_date_dimension(month_end(end_month))
    write_csv(dims["classrooms"], CURRENT / "Dimensions" / "Full_Classrooms.csv")
    write_csv(current_date_dimension, CURRENT / "Dimensions" / "Full_Date_Dimension_2021_2026.csv")
    write_csv(current_date_dimension, CURRENT / "Dimensions" / "Dim_Date.csv")
    write_csv(dims["districts"], CURRENT / "Dimensions" / "Full_Districts.csv")
    write_csv(dims["schools"], CURRENT / "Dimensions" / "Full_Schools.csv")
    write_csv(dims["users"], CURRENT / "Dimensions" / "Full_Users.csv")

    write_csv(facts["contracts"], CURRENT / "Facts" / "Full_Contracts.csv")
    write_csv(facts["hardware"], CURRENT / "Facts" / "Full_Hardware_Assets.csv")
    write_csv(facts["assignments"], CURRENT / "Facts" / "Full_License_Assignments.csv")
    write_csv(facts["purchase_header"], CURRENT / "Facts" / "Full_Purchases_Header.csv")
    write_csv(facts["purchase_lines"], CURRENT / "Facts" / "Full_Purchases_Lines.csv")
    write_csv(facts["software"], CURRENT / "Facts" / "Full_Software_Entitlements.csv")


def write_refresh_log(months: list[date], refresh_rows: list[dict[str, str]]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(refresh_rows)
    write_csv(summary, PROJECT_ROOT / "data" / "monthly_refresh_summary.csv")

    lines = [
        "# Monthly Refresh Log",
        "",
        "This log documents the recurring-data workflow for the Procurement & Contract Risk Dashboard.",
        "",
        "Baseline source: recovered 2021-2025 synthetic BOCES procurement CSVs.",
        "",
        f"Generated refresh range: {months[0].strftime('%Y-%m')} through {months[-1].strftime('%Y-%m')}.",
        "",
        "| Refresh Month | Purchase Orders | Purchase Lines | Hardware Assets | Software Entitlements | License Assignments | Contracts | Incremental Spend |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in refresh_rows:
        lines.append(
            "| {refresh_month} | {purchase_orders} | {purchase_lines} | {hardware_assets} | {software_entitlements} | {license_assignments} | {contracts} | ${incremental_spend} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Portfolio Talking Point",
            "",
            "Project 2 is staged as a recurring monthly procurement reporting process. The 2021-2025 dataset acts as the historical baseline, then each monthly close generates incremental procurement, contract, license, assignment, and hardware asset records. The Power BI model can refresh against the current folder while the monthly update folders preserve the audit trail.",
            "",
            "## Super / Notion Update Snippet",
            "",
            "Use this wording on the Project 2 case study page after screenshots are updated:",
            "",
            "> The dashboard uses a 2021-2025 synthetic education IT procurement baseline and a recurring monthly refresh process. January through April 2026 update packages were generated to simulate an operational reporting cadence, with purchase orders, contracts, software entitlements, license assignments, and hardware assets appended through a repeatable script.",
        ]
    )
    (DOCS / "monthly_refresh_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_outputs(facts: dict[str, pd.DataFrame], refresh_rows: list[dict[str, str]]) -> None:
    errors = []
    if facts["purchase_header"]["PO_ID"].duplicated().any():
        errors.append("Duplicate PO_ID values found.")
    if facts["contracts"]["Contract_ID"].duplicated().any():
        errors.append("Duplicate Contract_ID values found.")
    if facts["software"]["License_ID"].duplicated().any():
        errors.append("Duplicate License_ID values found.")
    if facts["hardware"]["Asset_ID"].duplicated().any():
        errors.append("Duplicate Asset_ID values found.")
    if facts["assignments"]["Assignment_ID"].duplicated().any():
        errors.append("Duplicate Assignment_ID values found.")

    known_po_ids = set(facts["purchase_header"]["PO_ID"])
    line_po_ids = set(facts["purchase_lines"]["PO_ID"])
    missing_po = line_po_ids - known_po_ids
    if missing_po:
        errors.append(f"{len(missing_po)} purchase line PO_ID values do not exist in purchase header.")

    if errors:
        raise ValueError("Validation failed: " + " ".join(errors))


def generate(start_month: str, end_month: str) -> None:
    dims = {name: read_csv(path) for name, path in DIM_FILES.items()}
    facts = {name: read_csv(path) for name, path in FACT_FILES.items()}
    state = initialize_state(facts)
    months = month_iter(start_month, end_month)
    refresh_rows: list[dict[str, str]] = []

    for month in months:
        rng = random.Random(int(f"{month.year}{month.month:02d}"))
        new_contracts = generate_contracts(month, facts, state, rng)
        new_headers, new_lines = generate_purchases(month, facts, state, rng, new_contracts)
        new_hardware = generate_hardware_assets(new_headers, new_lines, dims, facts, state, rng)
        new_software, new_assignments = generate_software_and_assignments(new_headers, new_lines, dims, facts, state, rng)

        increments = {
            "contracts": new_contracts,
            "purchase_header": new_headers,
            "purchase_lines": new_lines,
            "hardware": new_hardware,
            "software": new_software,
            "assignments": new_assignments,
        }
        write_month_package(month, dims, facts, increments)

        for key, inc in increments.items():
            facts[key] = pd.concat([facts[key], inc], ignore_index=True)

        incremental_spend = sum(to_float(v) for v in new_lines["Total_Spend"]) if not new_lines.empty else 0
        refresh_rows.append(
            {
                "refresh_month": f"{month.year}-{month.month:02d}",
                "purchase_orders": f"{len(new_headers):,}",
                "purchase_lines": f"{len(new_lines):,}",
                "hardware_assets": f"{len(new_hardware):,}",
                "software_entitlements": f"{len(new_software):,}",
                "license_assignments": f"{len(new_assignments):,}",
                "contracts": f"{len(new_contracts):,}",
                "incremental_spend": f"{incremental_spend:,.2f}",
            }
        )

    validate_outputs(facts, refresh_rows)
    write_current(dims, facts, months[-1])
    write_refresh_log(months, refresh_rows)

    print(f"Generated monthly refresh packages for {start_month} through {end_month}.")
    print(f"Current refresh-ready files written to: {CURRENT}")
    print(f"Refresh log written to: {DOCS / 'monthly_refresh_log.md'}")


def previous_month(today: date | None = None) -> str:
    today = today or date.today()
    first_this_month = today.replace(day=1)
    prev = first_this_month - timedelta(days=1)
    return f"{prev.year}-{prev.month:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate monthly Project 2 procurement refresh datasets.")
    parser.add_argument("--start-month", default="2026-01", help="First month to generate, format YYYY-MM.")
    parser.add_argument("--end-month", default=None, help="Last month to generate, format YYYY-MM.")
    parser.add_argument("--previous-month-only", action="store_true", help="Generate only the previous calendar month.")
    args = parser.parse_args()

    if args.previous_month_only:
        month = previous_month()
        generate(month, month)
    else:
        end_month = args.end_month or previous_month()
        generate(args.start_month, end_month)


if __name__ == "__main__":
    main()
