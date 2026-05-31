#!/usr/bin/env python3
"""Small public proof for a FlowOps Lab coding bounty / data task sprint.

This sample scores whether a public repo coding bounty or small data task has
enough acceptance criteria and scope detail for a same-day first slice.
Public wallet for USDT/USDC on EVM if commissioning a focused sprint:
0x8B9D88f5868B5D576524Abd53a4325F120e9aD2b
Use public or redacted samples only.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


SAMPLE_TASK = {
    "title": "Fix CSV import validation in public repo",
    "public_repo": "https://github.com/example/project",
    "issue_url": "https://github.com/example/project/issues/42",
    "task_type": "coding bounty data task",
    "acceptance_criteria": [
        "invalid rows are reported with row number and reason",
        "valid sample import still passes",
        "python3 -m pytest tests/test_import_validation.py passes",
    ],
    "payment_or_award_flow": "50 USDC on EVM after accepted first-slice patch",
    "sensitive_data_policy": "public or redacted samples only",
}


REQUIRED_FIELDS = {
    "title": 10,
    "public_repo": 20,
    "issue_url": 15,
    "acceptance_criteria": 25,
    "payment_or_award_flow": 20,
    "sensitive_data_policy": 10,
}


def has_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool([item for item in value if str(item).strip()])
    return value is not None


def score_task(task: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if not has_value(task.get(field))]
    score = sum(weight for field, weight in REQUIRED_FIELDS.items() if field not in missing)
    criteria = task.get("acceptance_criteria") or []
    if isinstance(criteria, list) and len(criteria) >= 2:
        score += 10
    if str(task.get("payment_or_award_flow", "")).lower().find("50") >= 0:
        score += 5
    score = min(score, 100)
    return {
        "score": score,
        "missing": missing,
        "ready_for_50_usdc_first_slice": score >= 80 and not missing,
        "recommended_next_step": (
            "confirm payment or award flow, then start a narrow patch"
            if score >= 80 and not missing
            else "collect missing scope fields before work starts"
        ),
    }


def run_self_test() -> None:
    report = score_task(SAMPLE_TASK)
    assert report["ready_for_50_usdc_first_slice"] is True
    assert report["score"] >= 80
    assert report["missing"] == []
    print("coding_bounty_fit_check_ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a small coding bounty or data task for first-slice readiness.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    report = score_task(SAMPLE_TASK)
    if args.json:
        print(json.dumps(report, indent=2))
        return
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
