from __future__ import annotations

import json
import os
import re
from pathlib import Path

from openai import OpenAI


# =========================================================
# OpenAI
# =========================================================

MODEL = os.getenv(
    "SUBTITLE_TRANSLATION_MODEL",
    "gpt-5.6-luna",
)

client = OpenAI()


# =========================================================
# Languages
# =========================================================

TARGET_LANGUAGES = {
    "en": "English",
    "ja": "Japanese",
    "zh-CN": "Simplified Chinese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}


# =========================================================
# SRT parser
# =========================================================

SRT_BLOCK_PATTERN = re.compile(
    r"""
    (?P<index>\d+)
    \s*
    (?P<timestamp>
        \d{2}:\d{2}:\d{2},\d{3}
        \s*-->\s*
        \d{2}:\d{2}:\d{2},\d{3}
    )
    \s*
    (?P<text>.*?)
    (?=\n\s*\n|\Z)
    """,
    re.VERBOSE | re.DOTALL,
)


def read_srt(path: Path) -> list[dict]:

    content = path.read_text(
        encoding="utf-8-sig"
    ).replace("\r\n", "\n")

    blocks = []

    for match in SRT_BLOCK_PATTERN.finditer(content):

        blocks.append(
            {
                "index": int(match.group("index")),
                "timestamp": match.group("timestamp").strip(),
                "text": match.group("text").strip(),
            }
        )

    if not blocks:
        raise ValueError(
            f"SRT parsing failed: {path}"
        )

    return blocks


# =========================================================
# Translation
# =========================================================

def translate_blocks(
    blocks: list[dict],
    language_code: str,
    language_name: str,
) -> list[str]:

    source_items = [
        {
            "id": block["index"],
            "text": block["text"],
        }
        for block in blocks
    ]

    prompt = f"""
Translate the following Korean YouTube subtitles into {language_name}.

This content is a Korean real-estate and economic news short-form video.

Requirements:

1. Translate naturally for native {language_name} viewers.
2. Preserve the factual meaning exactly.
3. Do not add or remove facts.
4. Keep real-estate, finance, policy, redevelopment,
   reconstruction, housing and government terminology accurate.
5. Keep proper nouns and place names recognizable.
6. Keep numbers, percentages, dates and monetary values accurate.
7. Make each subtitle concise enough to read during the
   original subtitle duration.
8. Do NOT translate mechanically word-for-word.
9. Return ONLY valid JSON.
10. Keep exactly the same IDs.

Return this structure:

{{
  "translations": [
    {{"id": 1, "text": "..."}},
    {{"id": 2, "text": "..."}}
  ]
}}

Source subtitles:

{json.dumps(source_items, ensure_ascii=False)}
""".strip()

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    raw = response.output_text.strip()

    # 혹시 모델이 ```json 을 붙이는 경우 제거
    if raw.startswith("```"):
        raw = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        )
        raw = re.sub(
            r"\s*```$",
            "",
            raw,
        )

    data = json.loads(raw)

    translations = data["translations"]

    translated_by_id = {
        int(item["id"]): item["text"].strip()
        for item in translations
    }

    result = []

    for block in blocks:

        index = block["index"]

        if index not in translated_by_id:
            raise ValueError(
                f"Missing translated subtitle ID "
                f"{index} ({language_code})"
            )

        result.append(
            translated_by_id[index]
        )

    return result


# =========================================================
# SRT writer
# =========================================================

def write_srt(
    output_path: Path,
    blocks: list[dict],
    translated_texts: list[str],
):

    lines = []

    for block, text in zip(
        blocks,
        translated_texts,
    ):

        lines.append(
            str(block["index"])
        )

        lines.append(
            block["timestamp"]
        )

        lines.append(
            text
        )

        lines.append("")

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8-sig",
    )


# =========================================================
# Public function
# =========================================================

def generate_multilingual_srt(
    korean_srt_path: str | Path,
) -> list[Path]:

    korean_srt_path = Path(
        korean_srt_path
    )

    if not korean_srt_path.exists():
        raise FileNotFoundError(
            korean_srt_path
        )

    print()
    print(
        "===================================="
    )
    print(
        "Generating Multilingual Subtitles"
    )
    print(
        "===================================="
    )

    print(
        f"[SRT] Source : "
        f"{korean_srt_path}"
    )

    blocks = read_srt(
        korean_srt_path
    )

    generated_files = []

    for language_code, language_name in (
        TARGET_LANGUAGES.items()
    ):

        print(
            f"[SRT] Translating: "
            f"{language_name}"
        )

        try:

            translated_texts = (
                translate_blocks(
                    blocks,
                    language_code,
                    language_name,
                )
            )

            output_path = (
                korean_srt_path.parent
                / (
                    f"{korean_srt_path.stem}_"
                    f"{language_code}"
                    f"{korean_srt_path.suffix}"
                )
            )

            write_srt(
                output_path,
                blocks,
                translated_texts,
            )

            generated_files.append(
                output_path
            )

            print(
                f"[OK] {language_code:5} : "
                f"{output_path}"
            )

        except Exception as exc:

            # 번역 하나가 실패해도
            # 전체 AP Daily가 죽지 않도록 함
            print(
                f"[WARN] Subtitle translation "
                f"failed ({language_code}): "
                f"{exc}"
            )

    print(
        "===================================="
    )

    return generated_files