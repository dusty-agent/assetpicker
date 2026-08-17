from pathlib import Path
import subprocess
import os
import shutil

from openai import OpenAI


# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parents[3]


# ==================================================
# FFmpeg
# ==================================================

if os.name == "nt":

    FFMPEG = (
        ROOT
        / "tools"
        / "ffmpeg"
        / "ffmpeg.exe"
    )

else:

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    FFMPEG = (
        Path(ffmpeg_path)
        if ffmpeg_path
        else None
    )


# ==================================================
# OpenAI
# ==================================================

client = OpenAI()


# ==================================================
# TTS Settings
# ==================================================

VOICE = "marin"

# AssetPicker 기본 나레이션 속도
TTS_SPEED = 1.15


# ==================================================
# FFmpeg Validation
# ==================================================

def require_ffmpeg():

    if FFMPEG is None:

        raise RuntimeError(
            "ffmpeg를 찾을 수 없습니다."
        )

    if not FFMPEG.exists():

        raise RuntimeError(
            "ffmpeg를 찾을 수 없습니다.\n"
            f"Expected: {FFMPEG}"
        )


# ==================================================
# TTS
# ==================================================

def generate_tts(
    text: str,
    output_path: Path,
) -> Path:

    require_ffmpeg()

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------
    # 혹시 이전 파일이 있으면 제거
    # --------------------------------------------------

    if output_path.exists():

        output_path.unlink()


    print(
        f"🎙️ TTS: "
        f"{output_path.name}"
    )


    # ==================================================
    # RAW Path
    # ==================================================

    raw_path = (
        output_path.with_name(
            f"{output_path.stem}_raw.mp3"
        )
    )


    if raw_path.exists():

        raw_path.unlink()


    try:

        # ==================================================
        # 1. OpenAI TTS
        # ==================================================

        with (
            client.audio.speech
            .with_streaming_response
            .create(
                model="gpt-4o-mini-tts",

                voice=VOICE,

                input=text,

                instructions=(
                    "20~30대의 밝고 자연스러운 "
                    "한국어 여성 진행자처럼 읽는다. "
                    "젊고 세련된 느낌으로 전달한다. "
                    "과하게 진지한 뉴스 앵커 톤은 피한다. "
                    "친근하지만 가볍지 않게 읽는다. "
                    "문장 사이의 쉼은 짧게 한다. "
                    "또렷하고 경쾌하게 발음한다."
                ),

                response_format="mp3",
            )
        ) as response:

            response.stream_to_file(
                raw_path
            )


        # ==================================================
        # 2. Speed Adjustment
        # ==================================================

        subprocess.run(
            [
                str(FFMPEG),

                "-y",

                "-i",
                str(raw_path),

                "-filter:a",
                f"atempo={TTS_SPEED}",

                "-vn",

                str(output_path),
            ],
            check=True,
        )


        print(
            f"   ⚡ "
            f"{TTS_SPEED}x speed"
        )


        return output_path


    finally:

        # ==================================================
        # 3. RAW Cleanup
        # ==================================================

        if raw_path.exists():

            raw_path.unlink()