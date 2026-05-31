#!/usr/bin/env python3
"""Small public proof for a FlowOps Lab sales performance analysis sprint.

This sample cleans a redacted sales CSV, flags duplicate opportunities, and
computes simple KPI totals. It is a data cleanup / KPI proof only.
Public wallet for USDT/USDC on EVM if commissioning a focused sprint:
0x8B9D88f5868B5D576524Abd53a4325F120e9aD2b
Use public or redacted samples only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from decimal import Decimal, InvalidOperation
from typing import Any


SAMPLE_CSV = """opportunity_id,owner,stage,amount,close_date,source
OPP-1001,Ada,Closed Won,"1,200.00",2026-05-03,website
OPP-1002,,Proposal,900,2026-05-11,partner
OPP-1003,Lin,Closed Lost,700,2026-05-15,website
OPP-1004,Ada,Closed Won,4400,2026-05-19,referral
OPP-1004,Ada,Closed Won,4400,2026-05-19,referral
"""


def parse_rows(lines: list[str]) -> list[dict[str, str]]:
    reader = csv.DictReader(lines)
    return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def parse_amount(value: str) -> Decimal:
    cleaned = value.replace(",", "").replace("$", "").strip()
    try:
        return Decimal(cleaned or "0")
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {value!r}") from exc


def clean_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        opportunity_id = row["opportunity_id"]
        duplicate = opportunity_id in seen
        seen.add(opportunity_id)
        cleaned.append(
            {
                "opportunity_id": opportunity_id,
                "owner": row["owner"] or "UNASSIGNED",
                "stage": row["stage"],
                "amount": parse_amount(row["amount"]),
                "close_date": row["close_date"],
                "source": row["source"],
                "duplicate": duplicate,
            }
        )
    return cleaned


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unique_rows = [row for row in rows if not row["duplicate"]]
    closed_won = [row for row in unique_rows if row["stage"].lower() == "closed won"]
    pipeline = [row for row in unique_rows if row["stage"].lower() not in {"closed won", "closed lost"}]
    closed_won_revenue = sum((row["amount"] for row in closed_won), Decimal("0"))
    pipeline_value = sum((row["amount"] for row in pipeline), Decimal("0"))
    return {
        "rows": len(rows),
        "unique_opportunities": len(unique_rows),
        "duplicate_rows": len(rows) - len(unique_rows),
        "missing_owner_rows": sum(1 for row in unique_rows if row["owner"] == "UNASSIGNED"),
        "closed_won_revenue": f"{closed_won_revenue:.2f}",
        "open_pipeline_value": f"{pipeline_value:.2f}",
        "recommended_checks": [
            "confirm duplicate opportunity ownership before deleting rows",
            "assign missing owners before KPI handoff",
            "separate closed-won revenue from open pipeline value",
        ],
    }


def run_self_test() -> None:
    rows = parse_rows(SAMPLE_CSV.splitlines())
    summary = summarize(clean_rows(rows))
    assert summary["closed_won_revenue"] == "5600.00"
    assert summary["duplicate_rows"] == 1
    assert summary["missing_owner_rows"] == 1
    print("sales_kpi_cleanup_check_ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a small sales CSV and summarize KPI checks.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    rows = parse_rows(io.StringIO(SAMPLE_CSV).read().splitlines())
    summary = summarize(clean_rows(rows))
    if args.json:
        print(json.dumps(summary, indent=2))
        return
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
