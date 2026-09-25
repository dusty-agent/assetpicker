from __future__ import annotations

from pathlib import Path

from googleapiclient.http import MediaFileUpload


CAPTION_TRACKS = {
    "": ("ko", "한국어"),
    "_en": ("en", "English"),
    "_es": ("es", "Español"),
    "_fr": ("fr", "Français"),
    "_de": ("de", "Deutsch"),
    "_ja": ("ja", "日本語"),
    "_zh-CN": ("zh-CN", "简体中文"),
}


def find_caption_files(video_path: Path):
    for suffix, (language, name) in CAPTION_TRACKS.items():
        caption_path = video_path.with_name(
            f"{video_path.stem}{suffix}.srt"
        )

        if caption_path.is_file():
            yield caption_path, language, name


def get_existing_tracks(
    youtube,
    video_id: str,
) -> set[tuple[str, str]]:
    response = youtube.captions().list(
        part="snippet",
        videoId=video_id,
    ).execute()

    return {
        (
            item["snippet"]["language"],
            item["snippet"]["name"],
        )
        for item in response.get("items", [])
    }


def upload_captions(
    youtube,
    video_id: str,
    video_path: Path,
) -> None:
    existing = get_existing_tracks(
        youtube,
        video_id,
    )

    uploaded = 0

    for caption_path, language, name in find_caption_files(
        video_path
    ):
        if (language, name) in existing:
            print(
                f"Caption already exists: "
                f"{language} / {name}"
            )
            continue

        youtube.captions().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "language": language,
                    "name": name,
                    "isDraft": False,
                }
            },
            media_body=MediaFileUpload(
                str(caption_path),
                mimetype="application/octet-stream",
                resumable=False,
            ),
        ).execute()

        print(
            f"Caption uploaded: "
            f"{language} / {name}"
        )

        uploaded += 1

    print(f"Captions uploaded: {uploaded}")