#!/usr/bin/env python3
"""
fitbit_fetch_wrapper.py
=======================
Reads per-user environment variables set by run.sh (using --user-index N)
and calls the original Fitbit Fetch logic with those credentials.

The original fitbit_fetch.py reads from environment variables, so this
wrapper simply sets the canonical names before importing / calling it.
"""

import argparse
import os
import sys


def load_user_env(index: int) -> None:
    """
    Copy the indexed env vars (e.g. FITBIT_USERNAME_0) into the canonical
    names that the original fitbit_fetch.py expects.
    """
    mapping = {
        f"FITBIT_USERNAME_{index}": "FITBIT_USERNAME",
        f"FITBIT_REFRESH_TOKEN_{index}": "FITBIT_REFRESH_TOKEN",
        f"FITBIT_CLIENT_ID_{index}": "FITBIT_CLIENT_ID",
        f"FITBIT_CLIENT_SECRET_{index}": "FITBIT_CLIENT_SECRET",
        f"FITBIT_DEVICENAME_{index}": "FITBIT_DEVICENAME",
        f"FITBIT_LOCAL_TIMEZONE_{index}": "FITBIT_LOCAL_TIMEZONE",
    }

    for src, dst in mapping.items():
        value = os.environ.get(src)
        if value is None:
            print(f"[ERROR] Missing env var: {src}", file=sys.stderr)
            sys.exit(1)
        os.environ[dst] = value
        print(f"[INFO] User {index}: {dst} = {'***' if 'TOKEN' in dst or 'SECRET' in dst else value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fitbit Fetch multi-user wrapper")
    parser.add_argument(
        "--user-index",
        type=int,
        required=True,
        help="Which user slot to read from environment (0-based)",
    )
    args = parser.parse_args()

    load_user_env(args.user_index)

    # Now that the canonical env vars are set, import and run the original fetcher.
    # The original script should be importable as a module OR we exec it.
    # Adjust the import path to match your repo layout.
    try:
        # Option A: if the original logic is in a function called main()
        import fitbit_fetch  # type: ignore
        fitbit_fetch.main()
    except AttributeError:
        # Option B: the original script runs at import time (no main guard)
        # In this case exec it directly – already handled by env vars being set.
        print(
            "[WARNING] fitbit_fetch.main() not found – "
            "ensure the original script has a main() entry point.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
