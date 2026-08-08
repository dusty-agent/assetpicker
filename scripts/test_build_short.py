from pathlib import Path

from app.daily.shorts.builder import (
    build_daily_short,
)


ROOT = Path(__file__).resolve().parents[1]


def main():

    date = "2026-08-08"

    daily_dir = (
        ROOT
        / "output"
        / "daily"
        / date
    )

    shorts_dir = (
        daily_dir
        / "shorts"
    )

    output_path = (
        daily_dir
        / f"ap_daily_short_{date}.mp4"
    )

    build_daily_short(
        date=date,
        source_dir=shorts_dir,
        output_path=output_path,
    )

    print()
    print("✅ Shorts rebuild complete")
    print(output_path)


if __name__ == "__main__":
    main()