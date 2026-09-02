from __future__ import annotations

import subprocess
import sys
from datetime import datetime


JOBS = [
    (
        "AP Daily",
        [sys.executable, "-m", "app.daily.main"],
    ),
    (
        "Development Update",
        [sys.executable, "-m", "app.development.main"],
    ),
    (
        "Market Reader",
        [sys.executable, "-m", "app.market_reader.main"],
    ),
]


def run_job(name: str, command: list[str]) -> bool:

    print()
    print("=" * 60)
    print(f"START : {name}")
    print("=" * 60)

    try:
        subprocess.run(
            command,
            check=True,
        )

        print()
        print(f"[OK] {name}")

        return True

    except subprocess.CalledProcessError as exc:

        print()
        print(f"[ERROR] {name}")
        print(f"Exit Code: {exc.returncode}")

        return False


def main():

    started_at = datetime.now()

    print()
    print("=" * 60)
    print("AssetPicker Morning Pipeline")
    print("=" * 60)
    print(
        "Started:",
        started_at.strftime("%Y-%m-%d %H:%M:%S"),
    )

    results = []

    for name, command in JOBS:

        success = run_job(
            name,
            command,
        )

        results.append(
            (name, success)
        )

    finished_at = datetime.now()

    print()
    print("=" * 60)
    print("MORNING PIPELINE COMPLETE")
    print("=" * 60)

    for name, success in results:

        status = (
            "OK"
            if success
            else "FAILED"
        )

        print(
            f"{status:<7} {name}"
        )

    print()
    print(
        "Finished:",
        finished_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )

    elapsed = (
        finished_at
        - started_at
    )

    print(
        f"Elapsed : "
        f"{elapsed.total_seconds():.1f}s"
    )

    print()

    failed = [
        name
        for name, success in results
        if not success
    ]

    if failed:

        print(
            "[WARN] Failed jobs:",
            ", ".join(failed),
        )

        sys.exit(1)


if __name__ == "__main__":
    main()