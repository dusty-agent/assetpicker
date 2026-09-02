from pathlib import Path


def format_srt_time(seconds: float) -> str:

    total_ms = round(
        max(0.0, seconds) * 1000
    )

    hours = total_ms // 3_600_000
    total_ms %= 3_600_000

    minutes = total_ms // 60_000
    total_ms %= 60_000

    secs = total_ms // 1000
    millis = total_ms % 1000

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02},"
        f"{millis:03}"
    )


def write_srt(
    cues: list[dict],
    output_path: Path,
) -> Path:

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    blocks = []

    for index, cue in enumerate(
        cues,
        start=1,
    ):

        text = str(
            cue.get("text", "")
        ).strip()

        if not text:
            continue

        start = float(
            cue["start"]
        )

        end = float(
            cue["end"]
        )

        blocks.append(
            "\n".join([
                str(index),
                (
                    f"{format_srt_time(start)}"
                    " --> "
                    f"{format_srt_time(end)}"
                ),
                text,
            ])
        )

    output_path.write_text(
        "\n\n".join(blocks) + "\n",
        encoding="utf-8-sig",
    )

    print(
        f"✅ SRT created: {output_path}"
    )

    return output_path