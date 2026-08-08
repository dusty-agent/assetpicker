from pathlib import Path
import subprocess
import os
import shutil


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

    ffmpeg_path = shutil.which("ffmpeg")

    FFMPEG = (
        Path(ffmpeg_path)
        if ffmpeg_path
        else None
    )


# ==================================================
# Audio Assets
# ==================================================

DEFAULT_BGM = (
    ROOT
    / "assets"
    / "bgm"
    / "ap_daily_theme.wav"
)

SHUTTER_SFX = (
    ROOT
    / "assets"
    / "sfx"
    / "shutter.mp3"
)

PAGE_FLIP_SFX = (
    ROOT
    / "assets"
    / "sfx"
    / "page_flip.mp3"
)

WHOOSH_SFX = (
    ROOT
    / "assets"
    / "sfx"
    / "whoosh.wav"
)


# ==================================================
# Audio Volume
# ==================================================

BGM_VOLUME = 0.30
SHUTTER_VOLUME = 0.14
PAGE_FLIP_VOLUME = 0.18
WHOOSH_VOLUME = 0.15


# ==================================================
# Video
# ==================================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30


# ==================================================
# Timeline
# ==================================================

DURATIONS = {

    "cover.png": 4.0,

    "introduction.png": 4.0,

    "issue_1.png": 5.0,
    "issue_2.png": 5.0,
    "issue_3.png": 5.0,
    "issue_4.png": 5.0,
    "issue_5.png": 5.0,

    "insight.png": 5.0,

    "ending.png": 4.0,
}


SLIDES = list(
    DURATIONS.keys()
)


TOTAL_DURATION = sum(
    DURATIONS.values()
)


# ==================================================
# Helpers
# ==================================================

def run(cmd):

    print()

    print(
        ">",
        " ".join(
            str(x)
            for x in cmd
        )
    )

    subprocess.run(
        cmd,
        check=True,
    )


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
# Validate Shorts PNG
# ==================================================

def validate_slides(
    source_dir: Path,
):

    if not source_dir.exists():

        raise FileNotFoundError(
            "쇼츠 이미지 폴더를 찾을 수 없습니다.\n"
            f"Expected: {source_dir}"
        )

    missing = []

    for filename in SLIDES:

        path = (
            source_dir
            / filename
        )

        if not path.exists():

            missing.append(
                filename
            )

    if missing:

        raise FileNotFoundError(
            "쇼츠 이미지가 부족합니다.\n"
            + "\n".join(
                missing
            )
        )


# ==================================================
# PNG → Clip
# ==================================================

def build_slide_clip(
    image_path: Path,
    filename: str,
    duration: float,
    output_path: Path,
):

    """
    1080 x 1920으로 완성된 쇼츠 PNG를
    해당 길이의 MP4 클립으로 만든다.

    Issue 1~5
        fade 없음

    Cover / Introduction / Insight / Ending
        짧은 fade in/out
    """

    fade_duration = 0.30

    fade_out_start = max(
        duration - fade_duration,
        0,
    )

    is_issue = filename.startswith(
        "issue_"
    )

    filters = [

        (
            f"scale="
            f"{WIDTH}:"
            f"{HEIGHT}:"
            f"flags=lanczos"
        )
    ]


    # --------------------------------------------------
    # Fade
    # --------------------------------------------------

    if not is_issue:

        filters.append(
            f"fade="
            f"t=in:"
            f"st=0:"
            f"d={fade_duration}"
        )

        filters.append(
            f"fade="
            f"t=out:"
            f"st={fade_out_start}:"
            f"d={fade_duration}"
        )


    filters.append(
        f"fps={FPS}"
    )

    filters.append(
        "format=yuv420p"
    )


    vf = ",".join(
        filters
    )


    cmd = [

        str(FFMPEG),

        "-y",

        "-loop",
        "1",

        "-i",
        str(image_path),

        "-t",
        str(duration),

        "-vf",
        vf,

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        str(output_path),
    ]


    run(cmd)


# ==================================================
# Concat
# ==================================================

def make_concat_file(
    clips: list[Path],
    concat_file: Path,
):

    lines = []

    for clip in clips:

        path = (
            clip
            .resolve()
            .as_posix()
        )

        lines.append(
            f"file '{path}'"
        )


    concat_file.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def concat_clips(
    clips: list[Path],
    output_path: Path,
):

    concat_file = (
        output_path.parent
        / "_concat.txt"
    )


    make_concat_file(
        clips,
        concat_file,
    )


    cmd = [

        str(FFMPEG),

        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat_file),

        "-c",
        "copy",

        "-movflags",
        "+faststart",

        str(output_path),
    ]


    run(cmd)


    concat_file.unlink(
        missing_ok=True
    )


# ==================================================
# Audio
# ==================================================

def build_audio(
    video_path: Path,
    output_path: Path,
):

    """
    Timeline

    00 Cover
    04 Introduction

    08 Issue 1  -> shutter
    13 Issue 2  -> page flip
    18 Issue 3  -> shutter
    23 Issue 4  -> page flip
    28 Issue 5  -> shutter

    33 Insight  -> whoosh

    38 Ending

    Total 42 sec
    """

    if not DEFAULT_BGM.exists():

        raise FileNotFoundError(
            "BGM 파일이 없습니다.\n"
            f"Expected: {DEFAULT_BGM}"
        )


    cmd = [

        str(FFMPEG),

        "-y",

        "-i",
        str(video_path),

        "-stream_loop",
        "-1",

        "-i",
        str(DEFAULT_BGM),
    ]


    filter_parts = []

    mix_inputs = [
        "[bgm]"
    ]


    # ==================================================
    # BGM
    # ==================================================

    fade_out_start = max(
        TOTAL_DURATION - 1.5,
        0,
    )


    filter_parts.append(

        "[1:a]"

        f"volume={BGM_VOLUME},"

        "afade="
        "t=in:"
        "st=0:"
        "d=0.6,"

        "afade="
        "t=out:"
        f"st={fade_out_start}:"
        "d=1.5"

        "[bgm]"
    )


    input_index = 2


    # ==================================================
    # Shutter
    # Issue 1 / 3 / 5
    # ==================================================

    shutter_times = [
        8.0,
        18.0,
        28.0,
    ]


    if SHUTTER_SFX.exists():

        cmd += [
            "-i",
            str(SHUTTER_SFX),
        ]


        for i, time_sec in enumerate(
            shutter_times
        ):

            delay_ms = int(
                time_sec * 1000
            )

            label = (
                f"shutter{i}"
            )


            filter_parts.append(

                f"[{input_index}:a]"

                f"adelay="
                f"{delay_ms}|"
                f"{delay_ms},"

                f"volume="
                f"{SHUTTER_VOLUME}"

                f"[{label}]"
            )


            mix_inputs.append(
                f"[{label}]"
            )


        input_index += 1


    # ==================================================
    # Page Flip
    # Issue 2 / 4
    # ==================================================

    page_flip_times = [
        13.0,
        23.0,
    ]


    if PAGE_FLIP_SFX.exists():

        cmd += [
            "-i",
            str(PAGE_FLIP_SFX),
        ]


        for i, time_sec in enumerate(
            page_flip_times
        ):

            delay_ms = int(
                time_sec * 1000
            )

            label = (
                f"pageflip{i}"
            )


            filter_parts.append(

                f"[{input_index}:a]"

                f"adelay="
                f"{delay_ms}|"
                f"{delay_ms},"

                f"volume="
                f"{PAGE_FLIP_VOLUME}"

                f"[{label}]"
            )


            mix_inputs.append(
                f"[{label}]"
            )


        input_index += 1


    # ==================================================
    # Insight Whoosh
    # ==================================================

    if WHOOSH_SFX.exists():

        cmd += [
            "-i",
            str(WHOOSH_SFX),
        ]


        delay_ms = 33000


        filter_parts.append(

            f"[{input_index}:a]"

            f"adelay="
            f"{delay_ms}|"
            f"{delay_ms},"

            f"volume="
            f"{WHOOSH_VOLUME}"

            "[whoosh]"
        )


        mix_inputs.append(
            "[whoosh]"
        )


    # ==================================================
    # Mix
    # ==================================================

    filter_parts.append(

        "".join(
            mix_inputs
        )

        + f"amix="
          f"inputs={len(mix_inputs)}:"
          f"duration=longest:"
          f"dropout_transition=0"

          "[audio]"
    )


    filter_complex = ";".join(
        filter_parts
    )


    cmd += [

        "-filter_complex",
        filter_complex,

        "-map",
        "0:v:0",

        "-map",
        "[audio]",

        "-c:v",
        "copy",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-t",
        str(TOTAL_DURATION),

        "-movflags",
        "+faststart",

        str(output_path),
    ]


    run(cmd)


# ==================================================
# Public Builder
# ==================================================

def build_daily_short(
    *,
    date: str,
    source_dir: Path,
    output_path: Path,
) -> Path:

    """
    AP Daily Shorts 영상 생성.

    Parameters
    ----------

    date
        YYYY-MM-DD

    source_dir
        완성된 1080x1920 쇼츠 PNG 9장 폴더

    output_path
        최종 MP4 저장 위치
    """

    require_ffmpeg()

    validate_slides(
        source_dir
    )


    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    temp_dir = (
        output_path.parent
        / "_short_temp"
    )


    # 혹시 이전 실행이 중단되어
    # temp가 남았다면 제거
    if temp_dir.exists():

        shutil.rmtree(
            temp_dir
        )


    temp_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    clips = []


    print()
    print(
        "===================================="
    )
    print(
        "AP Daily Shorts Builder"
    )
    print(
        "===================================="
    )

    print(
        f"Date       : {date}"
    )

    print(
        f"Source     : {source_dir}"
    )

    print(
        f"Output     : {output_path}"
    )

    print(
        f"Resolution : {WIDTH}x{HEIGHT}"
    )

    print(
        f"Duration   : {TOTAL_DURATION}s"
    )

    print()


    try:

        # ==================================================
        # 1. PNG → Clips
        # ==================================================

        for index, filename in enumerate(
            SLIDES,
            start=1,
        ):

            image_path = (
                source_dir
                / filename
            )

            duration = (
                DURATIONS[
                    filename
                ]
            )

            clip_path = (
                temp_dir
                / f"{index:02d}.mp4"
            )


            print(
                f"[{index}/{len(SLIDES)}] "
                f"{filename} "
                f"{duration:.1f}s"
            )


            build_slide_clip(
                image_path=image_path,
                filename=filename,
                duration=duration,
                output_path=clip_path,
            )


            clips.append(
                clip_path
            )


        # ==================================================
        # 2. Silent Video
        # ==================================================

        silent_output = (
            temp_dir
            / (
                f"ap_daily_short_"
                f"{date}_silent.mp4"
            )
        )


        concat_clips(
            clips=clips,
            output_path=silent_output,
        )


        # ==================================================
        # 3. Audio
        # ==================================================

        build_audio(
            video_path=silent_output,
            output_path=output_path,
        )


        print()
        print(
            "===================================="
        )
        print(
            "✅ AP Daily Short Complete"
        )
        print(
            "===================================="
        )
        print(
            output_path
        )
        print()


        return output_path


    finally:

        # ==================================================
        # Cleanup
        # ==================================================

        if temp_dir.exists():

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )