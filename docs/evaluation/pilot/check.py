#!/usr/bin/env python3
"""External functional checks for the fixed synthetic ACS pilot tasks."""
import argparse
from pathlib import Path
import runpy
import sys

FIXTURE = Path(__file__).resolve().parent / "fixture"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check(case, target):
    readme = (target / "README.md").read_bytes()
    if case == "simple":
        require(readme == (FIXTURE / "README.md").read_bytes().replace(
            b"# Report summmary\n", b"# Report summary\n", 1), "Correct only the heading typo")
        require((target / "report.py").read_bytes() == (FIXTURE / "report.py").read_bytes(),
                "Simple case must not modify report.py")
        return
    # This deliberately executes the candidate's local Python code, just like
    # running its tests. Only use disposable, reviewed pilot targets.
    module = runpy.run_path(str(target / "report.py"))
    total, can_read = module["total"], module["can_read"]
    rows = [
        {"category": "A", "amount": 10},
        {"category": "a", "amount": 2},
        {"category": "A", "amount": -3},
        {"category": "", "amount": -2},
    ]
    require(total(rows) == 7, "Existing total(rows) behaviour")
    require(total([]) == 0, "Empty total")
    if case == "normal":
        require(total(rows, category="A") == 7, "Exact category and negative amounts")
        require(total(rows, "a") == 2, "Case-sensitive category")
        require(total(rows, "") == -2, "Empty string is an exact category")
        require(total(rows, None) == 7, "None means all rows")
        require(total(rows, "missing") == 0, "No matching category")
        require(total([], "A") == 0, "Empty rows with category")
        # Check unchanged ordinary access behaviour; the separate complex
        # case addresses malformed and missing identifiers.
        require(can_read({"public": True, "owner": "a"}, None) is True, "Public access")
        require(can_read({"public": False, "owner": "a"}, "a") is True, "Owner access")
        require(can_read({"public": False, "owner": "a"}, "b") is False, "Other viewer denied")
    elif case == "complex":
        for row, viewer, expected in [
            ({"public": True}, None, True),
            ({"public": True, "owner": ""}, "b", True),
            ({"public": False, "owner": "a"}, "a", True),
            ({"public": False, "owner": "a"}, "A", False),
            ({"owner": "a"}, "a", True),
            ({"public": False, "owner": "a"}, None, False),
            ({"public": False}, None, False),
            ({}, None, False),
            ({"owner": ""}, "", False),
            ({"owner": 1}, 1, False),
            ({"owner": True}, True, False),
            ({"public": "yes", "owner": "a"}, "b", False),
            ({"public": 1}, None, False),
        ]:
            require(can_read(row, viewer) is expected, f"Access rule failed: {row!r}, {viewer!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("simple", "normal", "complex"))
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        check(args.case, args.target.resolve())
    except Exception as error:
        print(f"FAIL: {args.case}: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.case} functional checks only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
