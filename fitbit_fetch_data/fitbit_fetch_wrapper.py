#!/usr/bin/env python3
"""
fitbit_fetch_wrapper.py
=======================
Reads per-user environment variables set by run.sh (using --user-index N)
and calls the original Fitbit Fetch logic with those credentials.
Each user can have their own InfluxDB database/bucket.
"""

import argparse
import os
import sys


def load_user_env(index: int) -> None:
    mapping = {
        f"FITBIT_USERNAME_{index}": "FITBIT_USERNAME",
        f"FITBIT_REFRESH_TOKEN_{index}": "FITBIT_REFRESH_TOKEN",
        f"FITBIT_CLIENT_ID_{index}": "FITBIT_CLIENT_ID",
        f"FITBIT_CLIENT_SECRET_{index}": "FITBIT_CLIENT_SECRET",
        f"FITBIT_DEVICENAME_{index}": "FITBIT_DEVICENAME",
        f"FITBIT_LOCAL_TIMEZONE_{index}": "FITBIT_LOCAL_TIMEZONE",
        f"FITBIT_INFLUXDB_DATABASE_{index}": "INFLUXDB_DATABASE",  # override shared DB
    }

    for src, dst in mapping.items():
        value = os.environ.get(src)
        if value is None:
            print(f"[ERROR] Missing env var: {src}", file=sys.stderr)
            sys.exit(1)
        os.environ[dst] = value
        safe_val = "***" if any(x in dst for x in ["TOKEN", "SECRET", "PASSWORD"]) else value
        print(f"[INFO] User {index}: {dst} = {safe_val}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fitbit Fetch multi-user wrapper")
    parser.add_argument("--user-index", type=int, required=True)
    args = parser.parse_args()

    load_user_env(args.user_index)

    try:
        import fitbit_fetch  # type: ignore
        fitbit_fetch.main()
    except AttributeError:
        print(
            "[WARNING] fitbit_fetch.main() not found – "
            "ensure the original script has a main() entry point.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
