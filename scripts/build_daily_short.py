from pathlib import Path
from PIL import Image
import subprocess
import sys
import os
import shutil


ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------
# FFmpeg
# --------------------------------------------------

if os.name == "nt":
    FFMPEG = ROOT / "tools" / "ffmpeg" / "ffmpeg.exe"
    FFPROBE = ROOT / "tools" / "ffmpeg" / "ffprobe.exe"
else:
    FFMPEG = Path(shutil.which("ffmpeg") or "")
    FFPROBE = Path(shutil.which("ffprobe") or "")


# --------------------------------------------------
# Assets
# --------------------------------------------------

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
    / "page_flip.mp3" #"camera_shutter.mp3"
)

WHOOSH_SFX = (
    ROOT
    / "assets"
    / "sfx"
    / "whoosh.wav"
)


# --------------------------------------------------
# Video
# --------------------------------------------------

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# 카드 위치
CARD_Y = 170

# 총 42초
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

SLIDES = list(DURATIONS.keys())


# --------------------------------------------------
# 카드 바깥 배경색
#
# 기존 카드뉴스 색을 크게 벗어나지 않는
# 아주 미세한 남색 계열 변화
# --------------------------------------------------

BACKGROUND_COLORS = {
    "cover.png": "0x080D14",
    "introduction.png": "0x101927",

    "issue_1.png": "0x111C2C",
    "issue_2.png": "0x132033",
    "issue_3.png": "0x152337",
    "issue_4.png": "0x132033",
    "issue_5.png": "0x111C2C",

    "insight.png": "0x0E1725",
    "ending.png": "0x080D14",
}


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def run(cmd):
    print("\n>", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def require_ffmpeg():
    if not FFMPEG.exists():
        raise RuntimeError(
            "ffmpeg를 찾을 수 없습니다.\n"
            f"Expected: {FFMPEG}"
        )


# --------------------------------------------------
# Slide rendering
# --------------------------------------------------

def get_edge_colors(image_path: Path):
    """
    카드의 위쪽/아래쪽 가장자리 색을 읽어
    쇼츠 여백 확장 색으로 사용한다.
    """

    with Image.open(image_path).convert("RGB") as img:
        width, height = img.size

        # 가장 끝 1~2px은 border 등의 영향을 받을 수 있어서
        # 조금 안쪽 영역을 샘플링
        top_crop = img.crop(
            (0, 10, width, 50)
        )

        bottom_crop = img.crop(
            (0, height - 50, width, height - 10)
        )

        def average_color(crop):
            pixels = list(crop.resize((1, 1)).getdata())
            r, g, b = pixels[0]
            return f"0x{r:02X}{g:02X}{b:02X}"

        return (
            average_color(top_crop),
            average_color(bottom_crop),
        )

def build_slide_clip(
    image_path: Path,
    filename: str,
    duration: float,
    output_path: Path,
    slide_index: int,
):
    """
    기존 1080x1350 카드를
    1080x1920 쇼츠 프레임에 배치.

    - 카드 위/아래 실제 색상을 읽어 자연스럽게 확장
    - 원래의 부드러운 fade 전환 사용
    - Issue 페이지는 아주 약한 zoom
    """

    top_color, bottom_color = get_edge_colors(
        image_path
    )

    fade_duration = 0.30
    fade_out_start = max(
        duration - fade_duration,
        0,
    )

    bottom_y = CARD_Y + 1350
    bottom_height = HEIGHT - bottom_y

    is_issue = filename.startswith("issue_")

    filters = []

    # 카드 크기 유지
    filters.append(
        f"scale={WIDTH}:1350"
    )

    # # 3~7페이지 아주 약한 움직임
    # if is_issue:
    #     filters.append(
    #         "zoompan="
    #         "z='min(zoom+0.00008,1.01)':"
    #         "x='iw/2-(iw/zoom/2)':"
    #         "y='ih/2-(ih/zoom/2)':"
    #         "d=1:"
    #         f"s={WIDTH}x1350:"
    #         f"fps={FPS}"
    #     )

    # 우선 전체 9:16 캔버스 생성
    filters.append(
        f"pad={WIDTH}:{HEIGHT}:"
        f"0:{CARD_Y}:"
        "color=black"
    )

    # 카드 위쪽 → 카드 상단 실제 색
    filters.append(
        f"drawbox="
        f"x=0:y=0:"
        f"w={WIDTH}:h={CARD_Y}:"
        f"color={top_color}:"
        "t=fill"
    )

    # 카드 아래쪽 → 카드 하단 실제 색
    filters.append(
        f"drawbox="
        f"x=0:y={bottom_y}:"
        f"w={WIDTH}:h={bottom_height}:"
        f"color={bottom_color}:"
        "t=fill"
    )

    # Issue 1~5 (3~7페이지)는
    # 읽는 동안 화면 밝기가 변하지 않도록 전환 효과 없음
    if not is_issue:

        filters.append(
            f"fade=t=in:"
            f"st=0:"
            f"d={fade_duration}"
        )

        filters.append(
            f"fade=t=out:"
            f"st={fade_out_start}:"
            f"d={fade_duration}"
        )

    filters.append(
        f"fps={FPS}"
    )

    filters.append(
        "format=yuv420p"
    )

    vf = ",".join(filters)

    cmd = [
        str(FFMPEG),
        "-y",

        "-loop", "1",
        "-i", str(image_path),

        "-t", str(duration),

        "-vf", vf,

        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",

        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",

        str(output_path),
    ]

    run(cmd)

# --------------------------------------------------
# Concat
# --------------------------------------------------

def make_concat_file(
    clips,
    concat_file: Path,
):
    lines = []

    for clip in clips:
        path = clip.resolve().as_posix()
        lines.append(
            f"file '{path}'"
        )

    concat_file.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def concat_clips(
    clips,
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

        "-f", "concat",
        "-safe", "0",

        "-i", str(concat_file),

        "-c", "copy",

        "-movflags", "+faststart",

        str(output_path),
    ]

    run(cmd)

    concat_file.unlink(
        missing_ok=True
    )


# --------------------------------------------------
# Audio
# --------------------------------------------------

def build_audio(
    video_path: Path,
    output_path: Path,
):
    """
    BGM + SFX

    page 3~7:
        동일한 shutter sound

    page 8:
        whoosh sound (파일이 있을 때만)

    Timeline
    --------
    1 cover          0
    2 intro          4
    3 issue1         8
    4 issue2        13
    5 issue3        18
    6 issue4        23
    7 issue5        28
    8 insight       33
    9 ending        38
    """

    if not DEFAULT_BGM.exists():
        raise FileNotFoundError(
            "BGM 파일이 없습니다.\n"
            f"Expected: {DEFAULT_BGM}"
        )

    cmd = [
        str(FFMPEG),
        "-y",

        "-i", str(video_path),

        "-stream_loop", "-1",
        "-i", str(DEFAULT_BGM),
    ]

    filter_parts = []

    # BGM
    filter_parts.append(
        "[1:a]"
        "volume=0.30,"
        "afade=t=in:st=0:d=0.6,"
        "afade=t=out:st=40.5:d=1.5"
        "[bgm]"
    )

    mix_inputs = ["[bgm]"]

    input_index = 2

    # ----------------------------------------------
    # Camera shutter
    # pages 3~7
    # ----------------------------------------------

    shutter_times = [
        8.0,
        13.0,
        18.0,
        23.0,
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

            label = f"shutter{i}"

            filter_parts.append(
                f"[{input_index}:a]"
                f"adelay="
                f"{delay_ms}|{delay_ms},"
                f"volume=0.18"
                f"[{label}]"
            )

            mix_inputs.append(
                f"[{label}]"
            )

        input_index += 1

    # ----------------------------------------------
    # Insight Whoosh
    # page 8
    # ----------------------------------------------

    if WHOOSH_SFX.exists():

        cmd += [
            "-i",
            str(WHOOSH_SFX),
        ]

        delay_ms = 33000

        filter_parts.append(
            f"[{input_index}:a]"
            f"adelay="
            f"{delay_ms}|{delay_ms},"
            f"volume=0.15"
            f"[whoosh]"
        )

        mix_inputs.append(
            "[whoosh]"
        )

    # ----------------------------------------------
    # Mix
    # ----------------------------------------------

    filter_parts.append(
        "".join(mix_inputs)
        + f"amix="
          f"inputs={len(mix_inputs)}:"
          f"duration=longest:"
          f"dropout_transition=0"
          f"[audio]"
    )

    filter_complex = ";".join(
        filter_parts
    )

    cmd += [
        "-filter_complex",
        filter_complex,

        "-map", "0:v:0",
        "-map", "[audio]",

        "-c:v", "copy",

        "-c:a", "aac",
        "-b:a", "192k",

        "-t", "42",

        "-movflags",
        "+faststart",

        str(output_path),
    ]

    run(cmd)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    require_ffmpeg()

    if len(sys.argv) < 2:
        print(
            "사용법:\n"
            "python "
            "scripts\\build_daily_short.py "
            "2026-08-07"
        )

        sys.exit(1)

    date = sys.argv[1]

    daily_dir = (
        ROOT
        / "output"
        / "daily"
        / date
    )

    if not daily_dir.exists():
        raise FileNotFoundError(
            f"폴더가 없습니다: "
            f"{daily_dir}"
        )

    # PNG 확인
    for filename in SLIDES:

        image_path = (
            daily_dir
            / filename
        )

        if not image_path.exists():
            raise FileNotFoundError(
                f"파일이 없습니다: "
                f"{image_path}"
            )

    temp_dir = (
        daily_dir
        / "_short_temp"
    )

    temp_dir.mkdir(
        exist_ok=True
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
        "Date:",
        date
    )

    print(
        "Duration:",
        sum(
            DURATIONS.values()
        ),
        "seconds"
    )

    print(
        "BGM:",
        DEFAULT_BGM
    )

    print(
        "Shutter:",
        SHUTTER_SFX
        if SHUTTER_SFX.exists()
        else "Not installed"
    )

    print(
        "Whoosh:",
        WHOOSH_SFX
        if WHOOSH_SFX.exists()
        else "Not installed"
    )

    try:

        # ------------------------------------------
        # Slides
        # ------------------------------------------

        for index, filename in enumerate(
            SLIDES,
            start=1,
        ):

            image_path = (
                daily_dir
                / filename
            )

            duration = (
                DURATIONS[filename]
            )

            clip_path = (
                temp_dir
                / f"{index:02d}.mp4"
            )

            print(
                f"\n"
                f"[{index}/{len(SLIDES)}] "
                f"{filename} "
                f"/ {duration:.1f}s"
            )

            build_slide_clip(
                image_path=image_path,
                filename=filename,
                duration=duration,
                output_path=clip_path,
                slide_index=index,
            )

            clips.append(
                clip_path
            )

        # ------------------------------------------
        # Silent video
        # ------------------------------------------

        silent_output = (
            daily_dir
            / f"ap_daily_short_"
              f"{date}_silent.mp4"
        )

        concat_clips(
            clips=clips,
            output_path=silent_output,
        )

        # ------------------------------------------
        # Final audio
        # ------------------------------------------

        final_output = (
            daily_dir
            / f"ap_daily_short_"
              f"{date}.mp4"
        )

        build_audio(
            video_path=silent_output,
            output_path=final_output,
        )

        print()
        print(
            "===================================="
        )
        print("완료!")
        print(
            "===================================="
        )
        print(
            final_output
        )

    finally:

        if temp_dir.exists():

            for file in (
                temp_dir.iterdir()
            ):
                file.unlink(
                    missing_ok=True
                )

            temp_dir.rmdir()


if __name__ == "__main__":
    main()