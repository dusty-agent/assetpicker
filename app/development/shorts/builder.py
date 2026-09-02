from pathlib import Path
import subprocess
import os
import shutil

from utils.subtitles import write_srt

from utils.subtitle_translator import (
    generate_multilingual_srt,
)


# ==================================================
# Root
# ==================================================

ROOT = Path(__file__).resolve().parents[3]


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

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    ffprobe_path = shutil.which(
        "ffprobe"
    )

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

BGM_VOLUME = 0.13

NARRATION_VOLUME = 1.00

SHUTTER_VOLUME = 0.10
PAGE_FLIP_VOLUME = 0.12
WHOOSH_VOLUME = 0.10


# ==================================================
# BGM
# ==================================================

BGM_FADE_IN = 0.6
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
MIN_SUMMARY_DURATION = 4.0
MIN_ENDING_DURATION = 3.0


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
        ),
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
# Slides
# ==================================================

def build_slide_list(
    issue_count: int,
) -> list[str]:

    if issue_count < 1:

        raise ValueError(
            "Development Shorts는 "
            "이슈가 최소 1개 필요합니다."
        )

    return [

        "cover.png",

        "introduction.png",

        *[
            f"issue_{i}.png"
            for i in range(
                1,
                issue_count + 1,
            )
        ],

        "summary.png",

        "ending.png",
    ]


# ==================================================
# Narration Files
# ==================================================

def build_narration_files(
    issue_count: int,
) -> dict[str, str]:

    files = {

        "opening":
            "opening.mp3",
    }

    for i in range(
        1,
        issue_count + 1,
    ):

        files[
            f"issue_{i}"
        ] = (
            f"issue_{i}.mp3"
        )

    files[
        "summary"
    ] = (
        "summary.mp3"
    )

    files[
        "ending"
    ] = (
        "ending.mp3"
    )

    return files


# ==================================================
# Validate Shorts PNG
# ==================================================

def validate_slides(
    source_dir: Path,
    slides: list[str],
):

    if not source_dir.exists():

        raise FileNotFoundError(
            "쇼츠 이미지 폴더를 찾을 수 없습니다.\n"
            f"Expected: {source_dir}"
        )

    missing = [

        filename

        for filename
        in slides

        if not (
            source_dir
            / filename
        ).exists()
    ]

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
    narration_files: dict[str, str],
):

    if not narration_dir.exists():

        raise FileNotFoundError(
            "나레이션 폴더를 찾을 수 없습니다.\n"
            f"Expected: {narration_dir}"
        )

    missing = [

        filename

        for filename
        in narration_files.values()

        if not (
            narration_dir
            / filename
        ).exists()
    ]

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

    return float(
        value
    )


# ==================================================
# Build Durations
# ==================================================

def build_durations(
    *,
    narration_dir: Path,
    issue_count: int,
    narration_files: dict[str, str],
) -> dict[str, float]:

    # --------------------------------------------------
    # Opening
    # --------------------------------------------------

    opening_duration = (
        get_audio_duration(
            narration_dir
            / narration_files[
                "opening"
            ]
        )
    )

    opening_total = max(
        (
            opening_duration
            + CARD_PADDING
        ),
        (
            COVER_DURATION
            + MIN_INTRO_DURATION
        ),
    )

    durations = {

        "cover.png":
            COVER_DURATION,

        "introduction.png":
            (
                opening_total
                - COVER_DURATION
            ),
    }


    # --------------------------------------------------
    # Issues
    # --------------------------------------------------

    for i in range(
        1,
        issue_count + 1,
    ):

        key = (
            f"issue_{i}"
        )

        audio_duration = (
            get_audio_duration(
                narration_dir
                / narration_files[
                    key
                ]
            )
        )

        durations[
            f"issue_{i}.png"
        ] = max(
            (
                audio_duration
                + CARD_PADDING
            ),
            MIN_ISSUE_DURATION,
        )


    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    summary_duration = (
        get_audio_duration(
            narration_dir
            / narration_files[
                "summary"
            ]
        )
    )

    durations[
        "summary.png"
    ] = max(
        (
            summary_duration
            + CARD_PADDING
        ),
        MIN_SUMMARY_DURATION,
    )


    # --------------------------------------------------
    # Ending
    # --------------------------------------------------

    ending_duration = (
        get_audio_duration(
            narration_dir
            / narration_files[
                "ending"
            ]
        )
    )

    durations[
        "ending.png"
    ] = max(
        (
            ending_duration
            + ENDING_PADDING
        ),
        MIN_ENDING_DURATION,
    )


    return durations


# ==================================================
# Build Timeline
# ==================================================

def build_timeline(
    *,
    slides: list[str],
    durations: dict[str, float],
):

    starts = {}

    current_time = 0.0

    for filename in slides:

        starts[
            filename
        ] = current_time

        current_time += (
            durations[
                filename
            ]
        )

    return (
        starts,
        current_time,
    )


# ==================================================
# Subtitle Timeline
# ==================================================

def build_subtitle_cues(
    *,
    scripts: dict[str, str],
    narration_dir: Path,
    narration_files: dict[str, str],
    issue_count: int,
    starts: dict[str, float],
) -> list[dict]:

    narration_timeline = [

        (
            "opening",
            0.0,
        ),
    ]

    for i in range(
        1,
        issue_count + 1,
    ):

        narration_timeline.append(
            (
                f"issue_{i}",
                starts[
                    f"issue_{i}.png"
                ],
            )
        )

    narration_timeline.extend([

        (
            "summary",
            starts[
                "summary.png"
            ],
        ),

        (
            "ending",
            starts[
                "ending.png"
            ],
        ),
    ])


    subtitle_cues = []


    for (
        name,
        start_time,
    ) in narration_timeline:

        if name not in scripts:

            raise RuntimeError(
                "자막용 나레이션 대본이 없습니다.\n"
                f"Missing script: {name}"
            )

        text = str(
            scripts[
                name
            ]
        ).strip()

        if not text:

            raise RuntimeError(
                "자막용 나레이션 대본이 비어 있습니다.\n"
                f"Script: {name}"
            )

        narration_path = (

            narration_dir

            / narration_files[
                name
            ]
        )

        audio_duration = (
            get_audio_duration(
                narration_path
            )
        )

        subtitle_cues.append({

            "text":
                text,

            "start":
                start_time,

            "end":
                (
                    start_time
                    + audio_duration
                ),
        })


    return subtitle_cues


# ==================================================
# Print Timeline
# ==================================================

def print_timeline(
    *,
    slides: list[str],
    durations: dict[str, float],
    starts: dict[str, float],
    total_duration: float,
):

    print()

    print(
        "===================================="
    )

    print(
        "Development Dynamic Timeline"
    )

    print(
        "===================================="
    )

    print()


    for filename in slides:

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

    fade_duration = 0.30

    fade_out_start = max(
        (
            duration
            - fade_duration
        ),
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


    run(
        cmd
    )


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


    run(
        cmd
    )


    concat_file.unlink(
        missing_ok=True
    )


# ==================================================
# Delayed SFX
# ==================================================

def add_delayed_sfx(
    *,
    cmd: list,
    filter_parts: list[str],
    mix_inputs: list[str],
    input_index: int,
    sfx_path: Path,
    times: list[float],
    label_prefix: str,
    volume: float,
) -> int:

    if (
        not times
        or not sfx_path.exists()
    ):

        return input_index


    cmd += [

        "-i",
        str(sfx_path),
    ]


    for i, time_sec in enumerate(
        times
    ):

        delay_ms = int(
            time_sec
            * 1000
        )

        label = (
            f"{label_prefix}"
            f"{i}"
        )

        filter_parts.append(
            (
                f"[{input_index}:a]"
                f"adelay="
                f"{delay_ms}|"
                f"{delay_ms},"
                f"volume="
                f"{volume}"
                f"[{label}]"
            )
        )

        mix_inputs.append(
            f"[{label}]"
        )


    return (
        input_index
        + 1
    )


# ==================================================
# Audio
# ==================================================

def build_audio(
    *,
    video_path: Path,
    output_path: Path,
    narration_dir: Path,
    issue_count: int,
    narration_files: dict[str, str],
    durations: dict[str, float],
    starts: dict[str, float],
    total_duration: float,
):

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
        (
            total_duration
            - BGM_FADE_OUT
        ),
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
    # SFX
    # ==================================================

    shutter_times = [

        starts[
            f"issue_{i}.png"
        ]

        for i in range(
            1,
            issue_count + 1,
        )

        if i % 2 == 1
    ]


    page_flip_times = [

        starts[
            f"issue_{i}.png"
        ]

        for i in range(
            1,
            issue_count + 1,
        )

        if i % 2 == 0
    ]


    input_index = add_delayed_sfx(
        cmd=cmd,
        filter_parts=filter_parts,
        mix_inputs=mix_inputs,
        input_index=input_index,
        sfx_path=SHUTTER_SFX,
        times=shutter_times,
        label_prefix="shutter",
        volume=SHUTTER_VOLUME,
    )


    input_index = add_delayed_sfx(
        cmd=cmd,
        filter_parts=filter_parts,
        mix_inputs=mix_inputs,
        input_index=input_index,
        sfx_path=PAGE_FLIP_SFX,
        times=page_flip_times,
        label_prefix="pageflip",
        volume=PAGE_FLIP_VOLUME,
    )


    input_index = add_delayed_sfx(
        cmd=cmd,
        filter_parts=filter_parts,
        mix_inputs=mix_inputs,
        input_index=input_index,
        sfx_path=WHOOSH_SFX,
        times=[
            starts[
                "summary.png"
            ]
        ],
        label_prefix="whoosh",
        volume=WHOOSH_VOLUME,
    )


    # ==================================================
    # Narration Timeline
    # ==================================================

    narration_timeline = [

        (
            "opening",
            0.0,
        ),
    ]


    for i in range(
        1,
        issue_count + 1,
    ):

        narration_timeline.append(
            (
                f"issue_{i}",
                starts[
                    f"issue_{i}.png"
                ],
            )
        )


    narration_timeline.extend([

        (
            "summary",
            starts[
                "summary.png"
            ],
        ),

        (
            "ending",
            starts[
                "ending.png"
            ],
        ),
    ])


    for narration_number, (
        name,
        start_time,
    ) in enumerate(
        narration_timeline
    ):

        narration_path = (

            narration_dir

            / narration_files[
                name
            ]
        )


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


    run(
        cmd
    )


# ==================================================
# Public Builder
# ==================================================

def build_development_short(
    *,
    date: str,
    source_dir: Path,
    output_path: Path,
    issue_count: int,
    scripts: dict[str, str],
) -> Path:

    """
    AssetPicker Development Update 쇼츠 영상과
    YouTube 업로드용 SRT 자막을 생성합니다.

    issue_count는 1~5 가변입니다.


    Expected Structure
    ------------------

    shorts/
    ├─ card_shorts/
    │  ├─ cover.png
    │  ├─ introduction.png
    │  ├─ issue_1.png
    │  ├─ ...
    │  ├─ summary.png
    │  └─ ending.png
    │
    ├─ narration/
    │  ├─ opening.mp3
    │  ├─ issue_1.mp3
    │  ├─ ...
    │  ├─ summary.mp3
    │  └─ ending.mp3
    │
    ├─ development_update_YYYY-MM-DD.mp4
    └─ development_update_YYYY-MM-DD.srt
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


    shorts_root = (
        output_path.parent
    )


    narration_dir = (

        shorts_root

        / "narration"
    )


    # ==================================================
    # Slides / Narration
    # ==================================================

    slides = build_slide_list(
        issue_count
    )


    narration_files = (
        build_narration_files(
            issue_count
        )
    )


    # ==================================================
    # Validate Files
    # ==================================================

    validate_slides(
        source_dir,
        slides,
    )


    validate_narration(
        narration_dir,
        narration_files,
    )


    # ==================================================
    # Dynamic Durations
    # ==================================================

    durations = build_durations(
        narration_dir=narration_dir,
        issue_count=issue_count,
        narration_files=narration_files,
    )


    (
        starts,
        total_duration,
    ) = build_timeline(
        slides=slides,
        durations=durations,
    )


    # ==================================================
    # Subtitle Cues
    # ==================================================

    subtitle_cues = (
        build_subtitle_cues(
            scripts=scripts,
            narration_dir=narration_dir,
            narration_files=narration_files,
            issue_count=issue_count,
            starts=starts,
        )
    )


    # ==================================================
    # Timeline Info
    # ==================================================

    print_timeline(
        slides=slides,
        durations=durations,
        starts=starts,
        total_duration=total_duration,
    )


    # ==================================================
    # Output
    # ==================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    srt_path = (
        output_path
        .with_suffix(
            ".srt"
        )
    )


    # ==================================================
    # Temporary Directory
    # ==================================================

    temp_dir = (

        shorts_root

        / "_short_temp"
    )


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
        "Development Shorts Builder"
    )

    print(
        "===================================="
    )

    print(
        f"Date       : "
        f"{date}"
    )

    print(
        f"Issues     : "
        f"{issue_count}"
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
        f"Subtitle   : "
        f"{srt_path}"
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
            slides,
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
                f"{len(slides)}] "
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
                f"development_update_"
                f"{date}_silent.mp4"
            )
        )


        concat_clips(
            clips=clips,
            output_path=silent_output,
        )


        # ==================================================
        # 3. Audio Mix
        # ==================================================

        build_audio(
            video_path=silent_output,
            output_path=output_path,
            narration_dir=narration_dir,
            issue_count=issue_count,
            narration_files=narration_files,
            durations=durations,
            starts=starts,
            total_duration=total_duration,
        )


        # ==================================================
        # 4. YouTube SRT Subtitle
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
            "✅ Development Short Complete"
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

        if temp_dir.exists():

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )