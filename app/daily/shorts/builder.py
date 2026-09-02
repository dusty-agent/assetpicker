from pathlib import Path
import subprocess
import os
import shutil
from utils.subtitles import write_srt
import urllib3

from utils.subtitle_translator import (
    generate_multilingual_srt,
)

# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parents[3]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================================================
# FFmpeg / FFprobe
# ==================================================

if os.name == "nt":

    FFMPEG = (
        ROOT
        / "tools"
        / "ffmpeg"
        / "ffmpeg.exe"
    )

    FFPROBE = (
        ROOT
        / "tools"
        / "ffmpeg"
        / "ffprobe.exe"
    )

else:

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")

    FFMPEG = (
        Path(ffmpeg_path)
        if ffmpeg_path
        else None
    )

    FFPROBE = (
        Path(ffprobe_path)
        if ffprobe_path
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
#
# 나레이션이 들어가므로
# 기존 BGM 0.30 → 0.13으로 낮춤
#
# 나중에 귀로 듣고 이 값만 조절하면 됩니다.
# ==================================================

BGM_VOLUME = 0.13

NARRATION_VOLUME = 1.00

SHUTTER_VOLUME = 0.10
PAGE_FLIP_VOLUME = 0.12
WHOOSH_VOLUME = 0.10


# ==================================================
# BGM
# ==================================================

BGM_FADE_IN = 0.6

# 최종 영상 마지막 2초 동안
# 배경음악만 자연스럽게 fade out
BGM_FADE_OUT = 2.0


# ==================================================
# Video
# ==================================================

WIDTH = 1080
HEIGHT = 1920

FPS = 30


# ==================================================
# Timeline Settings
# ==================================================
#
# 이제 영상 길이는 고정하지 않습니다.
#
# narration mp3 길이
#       +
# CARD_PADDING
#
# 으로 카드별 길이를 자동 결정합니다.
# ==================================================

CARD_PADDING = 0.60

ENDING_PADDING = 0.80


# --------------------------------------------------
# Opening
#
# opening.mp3는
# Cover → Introduction
# 두 장에 걸쳐 계속 재생
# --------------------------------------------------

COVER_DURATION = 2.0

MIN_INTRO_DURATION = 1.5


# --------------------------------------------------
# 카드 최소 노출 시간
# --------------------------------------------------

MIN_ISSUE_DURATION = 4.0
MIN_INSIGHT_DURATION = 4.0
MIN_ENDING_DURATION = 3.0


# ==================================================
# Slides
# ==================================================

SLIDES = [

    "cover.png",
    "introduction.png",

    "issue_1.png",
    "issue_2.png",
    "issue_3.png",
    "issue_4.png",
    "issue_5.png",

    "insight.png",

    "ending.png",
]


# ==================================================
# Narration
# ==================================================

NARRATION_FILES = {

    "opening":
        "opening.mp3",

    "issue_1":
        "issue_1.mp3",

    "issue_2":
        "issue_2.mp3",

    "issue_3":
        "issue_3.mp3",

    "issue_4":
        "issue_4.mp3",

    "issue_5":
        "issue_5.mp3",

    "insight":
        "insight.mp3",

    "ending":
        "ending.mp3",
}


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


# ==================================================
# Validate FFmpeg
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

    if FFPROBE is None:

        raise RuntimeError(
            "ffprobe를 찾을 수 없습니다."
        )

    if not FFPROBE.exists():

        raise RuntimeError(
            "ffprobe를 찾을 수 없습니다.\n"
            f"Expected: {FFPROBE}"
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
# Validate Narration
# ==================================================

def validate_narration(
    narration_dir: Path,
):

    if not narration_dir.exists():

        raise FileNotFoundError(
            "나레이션 폴더를 찾을 수 없습니다.\n"
            f"Expected: {narration_dir}"
        )

    missing = []

    for filename in NARRATION_FILES.values():

        path = (
            narration_dir
            / filename
        )

        if not path.exists():

            missing.append(
                filename
            )

    if missing:

        raise FileNotFoundError(
            "나레이션 파일이 부족합니다.\n"
            + "\n".join(
                missing
            )
        )


# ==================================================
# Audio Duration
# ==================================================

def get_audio_duration(
    audio_path: Path,
) -> float:

    cmd = [

        str(FFPROBE),

        "-v",
        "error",

        "-show_entries",
        "format=duration",

        "-of",
        (
            "default="
            "noprint_wrappers=1:"
            "nokey=1"
        ),

        str(audio_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    value = (
        result.stdout
        .strip()
    )

    if not value:

        raise RuntimeError(
            "오디오 길이를 읽을 수 없습니다.\n"
            f"File: {audio_path}"
        )

    return float(value)


# ==================================================
# Build Durations
# ==================================================

def build_durations(
    narration_dir: Path,
) -> dict[str, float]:

    # --------------------------------------------------
    # Opening
    # --------------------------------------------------

    opening_duration = (
        get_audio_duration(
            narration_dir
            / NARRATION_FILES["opening"]
        )
    )

    # opening 전체 길이에 여유 추가
    opening_total = (
        opening_duration
        + CARD_PADDING
    )

    # 최소한
    # cover 2초 + intro 1.5초
    opening_total = max(
        opening_total,
        (
            COVER_DURATION
            + MIN_INTRO_DURATION
        ),
    )

    introduction_duration = (
        opening_total
        - COVER_DURATION
    )


    # --------------------------------------------------
    # Durations
    # --------------------------------------------------

    durations = {

        "cover.png":
            COVER_DURATION,

        "introduction.png":
            introduction_duration,
    }


    # --------------------------------------------------
    # Issues
    # --------------------------------------------------

    for i in range(
        1,
        6,
    ):

        key = (
            f"issue_{i}"
        )

        filename = (
            NARRATION_FILES[
                key
            ]
        )

        audio_duration = (
            get_audio_duration(
                narration_dir
                / filename
            )
        )

        card_duration = max(
            audio_duration
            + CARD_PADDING,
            MIN_ISSUE_DURATION,
        )

        durations[
            f"issue_{i}.png"
        ] = card_duration


    # --------------------------------------------------
    # Insight
    # --------------------------------------------------

    insight_audio_duration = (
        get_audio_duration(
            narration_dir
            / NARRATION_FILES["insight"]
        )
    )

    durations[
        "insight.png"
    ] = max(
        insight_audio_duration
        + CARD_PADDING,
        MIN_INSIGHT_DURATION,
    )


    # --------------------------------------------------
    # Ending
    # --------------------------------------------------

    ending_audio_duration = (
        get_audio_duration(
            narration_dir
            / NARRATION_FILES["ending"]
        )
    )

    durations[
        "ending.png"
    ] = max(
        ending_audio_duration
        + ENDING_PADDING,
        MIN_ENDING_DURATION,
    )


    return durations


# ==================================================
# Build Timeline
# ==================================================

def build_timeline(
    durations: dict[str, float],
):

    starts = {}

    current_time = 0.0

    for filename in SLIDES:

        starts[
            filename
        ] = current_time

        current_time += (
            durations[
                filename
            ]
        )

    total_duration = (
        current_time
    )

    return (
        starts,
        total_duration,
    )


# ==================================================
# Build Subtitle Cues
# ==================================================

def build_subtitle_cues(
    *,
    scripts: dict[str, str],
    narration_dir: Path,
    starts: dict[str, float],
) -> list[dict]:

    narration_timeline = [
        ("opening", 0.0),

        ("issue_1", starts["issue_1.png"]),
        ("issue_2", starts["issue_2.png"]),
        ("issue_3", starts["issue_3.png"]),
        ("issue_4", starts["issue_4.png"]),
        ("issue_5", starts["issue_5.png"]),

        ("insight", starts["insight.png"]),
        ("ending", starts["ending.png"]),
    ]

    subtitle_cues = []

    for name, start_time in narration_timeline:

        if name not in scripts:
            raise RuntimeError(
                "자막용 나레이션 대본이 없습니다.\n"
                f"Missing script: {name}"
            )

        text = str(
            scripts[name]
        ).strip()

        if not text:
            raise RuntimeError(
                "자막용 나레이션 대본이 비어 있습니다.\n"
                f"Script: {name}"
            )

        narration_path = (
            narration_dir
            / NARRATION_FILES[name]
        )

        audio_duration = get_audio_duration(
            narration_path
        )

        subtitle_cues.append({
            "text": text,
            "start": start_time,
            "end": start_time + audio_duration,
        })

    return subtitle_cues

# ==================================================
# Print Timeline
# ==================================================

def print_timeline(
    durations: dict[str, float],
    starts: dict[str, float],
    total_duration: float,
):

    print()
    print("====================================")
    print("Dynamic Timeline")
    print("====================================")
    print()

    for filename in SLIDES:

        start = (
            starts[
                filename
            ]
        )

        duration = (
            durations[
                filename
            ]
        )

        end = (
            start
            + duration
        )

        print(
            f"{filename:<18} "
            f"{start:6.2f}s"
            f" → "
            f"{end:6.2f}s "
            f"({duration:5.2f}s)"
        )

    print()
    print(
        f"TOTAL : "
        f"{total_duration:.2f}s"
    )
    print()


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
    1080 x 1920 쇼츠 PNG를
    지정된 길이의 MP4 clip으로 변환합니다.

    Issue 1~5:
        fade 없음

    Cover / Introduction / Insight / Ending:
        짧은 fade in/out
    """

    fade_duration = 0.30

    fade_out_start = max(
        duration
        - fade_duration,
        0,
    )

    is_issue = (
        filename.startswith(
            "issue_"
        )
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
            (
                "fade="
                "t=in:"
                "st=0:"
                f"d={fade_duration}"
            )
        )

        filters.append(
            (
                "fade="
                "t=out:"
                f"st={fade_out_start}:"
                f"d={fade_duration}"
            )
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
# Concat File
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
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )


# ==================================================
# Concat Clips
# ==================================================

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
    *,
    video_path: Path,
    output_path: Path,
    narration_dir: Path,
    durations: dict[str, float],
    starts: dict[str, float],
    total_duration: float,
):

    """
    최종 Audio Mix

    Video
    +
    BGM
    +
    Narration
    +
    SFX

    BGM은 짧아도 자동 loop되며
    영상 마지막 BGM_FADE_OUT초 동안
    fade out 됩니다.
    """

    if not DEFAULT_BGM.exists():

        raise FileNotFoundError(
            "BGM 파일이 없습니다.\n"
            f"Expected: {DEFAULT_BGM}"
        )


    # ==================================================
    # Inputs
    # ==================================================

    cmd = [

        str(FFMPEG),

        "-y",

        # --------------------------------------------------
        # Input 0
        # Video
        # --------------------------------------------------

        "-i",
        str(video_path),

        # --------------------------------------------------
        # Input 1
        # BGM
        #
        # -stream_loop -1
        # BGM이 끝나면 처음부터 다시 반복
        # --------------------------------------------------

        "-stream_loop",
        "-1",

        "-i",
        str(DEFAULT_BGM),
    ]


    filter_parts = []

    mix_inputs = []


    # ==================================================
    # BGM
    # ==================================================

    fade_out_start = max(
        total_duration
        - BGM_FADE_OUT,
        0,
    )


    filter_parts.append(

        (
            "[1:a]"
            f"volume={BGM_VOLUME},"
            f"atrim=0:{total_duration},"
            "asetpts=N/SR/TB,"
            "afade="
            "t=in:"
            "st=0:"
            f"d={BGM_FADE_IN},"
            "afade="
            "t=out:"
            f"st={fade_out_start}:"
            f"d={BGM_FADE_OUT}"
            "[bgm]"
        )
    )

    mix_inputs.append(
        "[bgm]"
    )


    input_index = 2


    # ==================================================
    # Shutter
    # Issue 1 / 3 / 5
    # ==================================================

    shutter_times = [

        starts[
            "issue_1.png"
        ],

        starts[
            "issue_3.png"
        ],

        starts[
            "issue_5.png"
        ],
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
                time_sec
                * 1000
            )

            label = (
                f"shutter{i}"
            )

            filter_parts.append(

                (
                    f"[{input_index}:a]"
                    f"adelay="
                    f"{delay_ms}|"
                    f"{delay_ms},"
                    f"volume="
                    f"{SHUTTER_VOLUME}"
                    f"[{label}]"
                )
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

        starts[
            "issue_2.png"
        ],

        starts[
            "issue_4.png"
        ],
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
                time_sec
                * 1000
            )

            label = (
                f"pageflip{i}"
            )

            filter_parts.append(

                (
                    f"[{input_index}:a]"
                    f"adelay="
                    f"{delay_ms}|"
                    f"{delay_ms},"
                    f"volume="
                    f"{PAGE_FLIP_VOLUME}"
                    f"[{label}]"
                )
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

        delay_ms = int(
            starts[
                "insight.png"
            ]
            * 1000
        )

        filter_parts.append(

            (
                f"[{input_index}:a]"
                f"adelay="
                f"{delay_ms}|"
                f"{delay_ms},"
                f"volume="
                f"{WHOOSH_VOLUME}"
                "[whoosh]"
            )
        )

        mix_inputs.append(
            "[whoosh]"
        )

        input_index += 1


    # ==================================================
    # Narration
    # ==================================================

    narration_timeline = [

        (
            "opening",
            0.0,
        ),

        (
            "issue_1",
            starts["issue_1.png"],
        ),

        (
            "issue_2",
            starts["issue_2.png"],
        ),

        (
            "issue_3",
            starts["issue_3.png"],
        ),

        (
            "issue_4",
            starts["issue_4.png"],
        ),

        (
            "issue_5",
            starts["issue_5.png"],
        ),

        (
            "insight",
            starts["insight.png"],
        ),

        (
            "ending",
            starts["ending.png"],
        ),
    ]


    for narration_number, (
        name,
        start_time,
    ) in enumerate(
        narration_timeline
    ):

        narration_path = (
            narration_dir
            / NARRATION_FILES[
                name
            ]
        )


        # --------------------------------------------------
        # Narration input
        # --------------------------------------------------

        cmd += [

            "-i",
            str(narration_path),
        ]


        delay_ms = int(
            start_time
            * 1000
        )

        label = (
            f"narration"
            f"{narration_number}"
        )


        filter_parts.append(

            (
                f"[{input_index}:a]"
                f"adelay="
                f"{delay_ms}|"
                f"{delay_ms},"
                f"volume="
                f"{NARRATION_VOLUME}"
                f"[{label}]"
            )
        )


        mix_inputs.append(
            f"[{label}]"
        )

        input_index += 1


    # ==================================================
    # Mix
    # ==================================================

    filter_parts.append(

        (
            "".join(
                mix_inputs
            )

            + (
                f"amix="
                f"inputs="
                f"{len(mix_inputs)}:"
                f"duration=longest:"
                f"dropout_transition=0:"
                f"normalize=0,"
                f"alimiter="
                f"limit=0.95"
                f"[audio]"
            )
        )
    )


    filter_complex = ";".join(
        filter_parts
    )


    # ==================================================
    # Output
    # ==================================================

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
        str(total_duration),

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
    scripts: dict[str, str],
) -> Path:

    """
    AP Daily Shorts 영상 생성.


    Expected Structure
    ------------------

    output/
    └─ daily/
       └─ YYYY-MM-DD/
          └─ shorts/
             ├─ card_shorts/
             │  ├─ cover.png
             │  ├─ introduction.png
             │  ├─ issue_1.png
             │  ├─ ...
             │  └─ ending.png
             │
             ├─ narration/
             │  ├─ opening.mp3
             │  ├─ issue_1.mp3
             │  ├─ ...
             │  └─ ending.mp3
             │
             └─ ap_daily_short_YYYY-MM-DD.mp4


    Parameters
    ----------

    date
        YYYY-MM-DD

    source_dir
        shorts/card_shorts

    output_path
        shorts/ap_daily_short_YYYY-MM-DD.mp4
    """


    # ==================================================
    # Validate Tools
    # ==================================================

    require_ffmpeg()


    # ==================================================
    # Paths
    # ==================================================

    source_dir = Path(
        source_dir
    )

    output_path = Path(
        output_path
    )


    # --------------------------------------------------
    # output_path.parent == shorts/
    # --------------------------------------------------

    shorts_root = (
        output_path.parent
    )

    narration_dir = (
        shorts_root
        / "narration"
    )


    # ==================================================
    # Validate Files
    # ==================================================

    validate_slides(
        source_dir
    )

    validate_narration(
        narration_dir
    )


    # ==================================================
    # Dynamic Durations
    # ==================================================

    durations = (
        build_durations(
            narration_dir
        )
    )


    (
        starts,
        total_duration,
    ) = build_timeline(
        durations
    )
    
    # ==================================================
    # Subtitle Cues
    # ==================================================

    subtitle_cues = build_subtitle_cues(
        scripts=scripts,
        narration_dir=narration_dir,
        starts=starts,
    )

    srt_path = (
        output_path
        .with_suffix(".srt")
    )


    print_timeline(
        durations,
        starts,
        total_duration,
    )


    # ==================================================
    # Output
    # ==================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ==================================================
    # Temporary Directory
    # ==================================================

    temp_dir = (
        shorts_root
        / "_short_temp"
    )


    # 이전 실행이 중단되어
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


    # ==================================================
    # Information
    # ==================================================

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
        f"Date       : "
        f"{date}"
    )

    print(
        f"Source     : "
        f"{source_dir}"
    )

    print(
        f"Narration  : "
        f"{narration_dir}"
    )

    print(
        f"Output     : "
        f"{output_path}"
    )

    print(
        f"Resolution : "
        f"{WIDTH}x{HEIGHT}"
    )

    print(
        f"Duration   : "
        f"{total_duration:.2f}s"
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
                durations[
                    filename
                ]
            )

            clip_path = (
                temp_dir
                / f"{index:02d}.mp4"
            )


            print(
                f"[{index}/"
                f"{len(SLIDES)}] "
                f"{filename} "
                f"{duration:.2f}s"
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
            narration_dir=narration_dir,
            durations=durations,
            starts=starts,
            total_duration=total_duration,
        )
        
        # ==================================================
        # 4. YouTube Subtitle
        # ==================================================

        write_srt(
            subtitle_cues,
            srt_path,
        )
        
        generate_multilingual_srt(
            srt_path
        )       


        # ==================================================
        # Complete
        # ==================================================

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
            f"Duration : "
            f"{total_duration:.2f}s"
        )

        print(
            f"Video    : "
            f"{output_path}"
        )

        print(
            f"Subtitle : "
            f"{srt_path}"
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