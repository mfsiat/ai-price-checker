#!/usr/bin/env python3
"""Validate the pricing dataset and (optionally) check its freshness.

This is the authoritative, server-side guard for the pricing data lifecycle.
It reuses the exact validation the app runs at startup, so CI fails on a bad
edit before it can be deployed.

Usage (from the ``backend`` directory)::

    python -m scripts.validate_pricing                    # structure only
    python -m scripts.validate_pricing --max-age-days 120 # also fail if stale

Exit codes: 0 = OK, 1 = invalid structure, 2 = stale data.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

# Allow running as a plain script (python scripts/validate_pricing.py) by
# ensuring the backend root (which contains the `app` package) is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import PricingDataError, PricingRepository  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate pricing data.")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=None,
        help="Fail if pricing last_updated is older than this many days.",
    )
    args = parser.parse_args(argv)

    try:
        repo = PricingRepository()
    except (PricingDataError, FileNotFoundError, ValueError) as exc:
        print(f"✗ Pricing data is invalid: {exc}", file=sys.stderr)
        return 1

    meta = repo.metadata()
    print(
        f"✓ Pricing valid: {meta['model_count']} models across "
        f"{meta['provider_count']} providers "
        f"(version={meta['version']}, last_updated={meta['last_updated']})"
    )

    if args.max_age_days is not None:
        last_updated = repo.last_updated
        if not last_updated:
            print("✗ No last_updated field to check freshness against.", file=sys.stderr)
            return 2
        try:
            updated = datetime.strptime(last_updated, "%Y-%m-%d").date()
        except ValueError:
            print(f"✗ last_updated '{last_updated}' is not an ISO date.", file=sys.stderr)
            return 2
        age = (date.today() - updated).days
        if age > args.max_age_days:
            print(
                f"✗ Pricing is stale: {age} days old (> {args.max_age_days}). "
                "Refresh backend/app/pricing.json. See docs/PRICING.md.",
                file=sys.stderr,
            )
            return 2
        print(f"✓ Pricing freshness OK: {age} days old.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
