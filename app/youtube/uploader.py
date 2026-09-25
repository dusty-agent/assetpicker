from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .captions import upload_captions


ROOT = Path(__file__).resolve().parents[2]

TOKEN_FILE = ROOT / ".secrets" / "youtube_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

KST = ZoneInfo("Asia/Seoul")

# YouTube에 공개 업로드를 요청한다.
# 단, 미검증 API 프로젝트는 Google 정책상 비공개로 제한될 수 있다.
PRIVACY_STATUS = "public"


VIDEO_CONFIGS = {
    "ap_daily": {
        "title": (
            "🏠 부동산뉴스 오늘 핵심 TOP5 "
            "| AP Daily | {display_date}"
        ),
        "description": """오늘 꼭 알아야 할 부동산 주요 뉴스를 40초로 정리했습니다.

✔ 정책
✔ 재건축
✔ 시장
✔ 청약
✔ 부동산 이슈

매일 아침 AI Editor Dustie가 Google News를 기반으로
핵심 뉴스만 빠르게 브리핑합니다.

오늘의 카드뉴스와 자세한 내용은
인스타그램에서도 확인하실 수 있습니다.

Instagram
https://instagram.com/assetpicker

💬 AssetPicker 부동산 정보 오픈채팅
매일 주요 부동산 뉴스와 시장 정보를 함께 확인하세요.
https://open.kakao.com/o/giaqO4Ii

#부동산 #부동산뉴스 #부동산투자 #재건축 #청약 #아파트 #부동산시장 #AssetPicker #APDaily
""",
        "tags": [
            "부동산",
            "부동산뉴스",
            "오늘의부동산뉴스",
            "부동산뉴스오늘",
            "부동산시장",
            "부동산이슈",
            "부동산정책",
            "부동산정보",
            "아파트",
            "아파트시장",
            "집값",
            "주택시장",
            "주택정책",
            "재건축",
            "재개발",
            "정비사업",
            "청약",
            "아파트청약",
            "분양",
            "분양시장",
            "부동산세금",
            "부동산대책",
            "국토교통부",
            "서울부동산",
            "서울아파트",
            "수도권부동산",
            "부동산브리핑",
            "뉴스브리핑",
            "데일리뉴스",
            "경제뉴스",
            "부동산쇼츠",
            "APDaily",
            "AssetPicker",
            "Dustie",
            "shorts",
            "youtube shorts",
        ],
        "video_path": (
            ROOT
            / "output"
            / "daily"
            / "{stamp}"
            / "shorts"
            / "ap_daily_short_{stamp}.mp4"
        ),
        "playlists": [
            "AP Daily",
            "AP Daily | 오늘의 부동산 주요뉴스",
        ],
    },

    "development": {
        "title": (
            "🏗️ 오늘의 정비사업 업데이트 TOP5 "
            "| {display_date}"
        ),
        "description": """오늘 꼭 확인해야 할 정비사업·주택개발 주요 업데이트를 짧게 정리했습니다.

✔ 재개발
✔ 재건축
✔ 신축/주택건설
✔ 시공자 선정
✔ 정책 변화

매일 아침 AssetPicker가 공식 자료를 기반으로
전국 정비사업과 개발 관련 핵심 변화만 빠르게 브리핑합니다.

오늘 영상은 아래 공식 출처를 바탕으로 제작했습니다.
- 토지이음
- 서울시 정비사업 정보몽땅
- 국토교통부

오늘의 카드뉴스와 자세한 내용은
인스타그램에서도 확인하실 수 있습니다.

Instagram
https://instagram.com/assetpicker

💬 AssetPicker 부동산 정보 오픈채팅
매일 주요 부동산 뉴스와 시장 정보를 함께 확인하세요.
https://open.kakao.com/o/giaqO4Ii

#부동산 #정비사업 #재개발 #재건축 #신축 #주택정책 #AssetPicker #APDaily
""",
        "tags": [
            "부동산",
            "부동산뉴스",
            "오늘의부동산뉴스",
            "정비사업",
            "오늘의정비사업",
            "정비사업뉴스",
            "재개발",
            "재건축",
            "신축",
            "주택건설",
            "주택건설사업계획",
            "사업계획승인",
            "시공자선정",
            "사업시행인가",
            "관리처분인가",
            "정비구역지정",
            "주택정책",
            "주택공급",
            "공급정책",
            "부동산정책",
            "개발사업",
            "도시정비",
            "도시개발",
            "아파트개발",
            "재개발뉴스",
            "재건축뉴스",
            "부동산이슈",
            "부동산브리핑",
            "뉴스브리핑",
            "데일리뉴스",
            "부동산쇼츠",
            "APDaily",
            "AssetPicker",
            "Development Update",
            "shorts",
            "youtube shorts",
        ],
        "video_path": (
            ROOT
            / "output"
            / "development"
            / "{stamp}"
            / "shorts"
            / "development_update_{stamp}.mp4"
        ),
        "playlists": [
            "AP Daily",
            "AP Daily | Development Update",
        ],
    },

    "market_reader": {
        "title": (
            "📊 오늘 환율·금리 "
            "| 원달러·엔화·유로 환율 | {display_date}"
        ),
        "description": """※ 주말 및 공휴일에는 환율 고시가 없어 가장 최근 영업일 기준 데이터를 사용합니다.

오늘 꼭 확인할 주요 시장 숫자를 20초로 정리했습니다.

✔ USD/KRW
✔ JPY/KRW
✔ EUR/KRW
✔ 수은채 유통수익률
✔ 주요 만기별 금리

한국수출입은행 공식 데이터를 기반으로
확인 가능한 최신 환율과 수은채 유통수익률을 정리합니다.

각 데이터의 기준일은 영상 내에 표시됩니다.

MarketReader는 시장 해석이나 전망이 아닌
주요 숫자를 간결하게 보여주는 데일리 마켓 보드입니다.

AssetPicker
Instagram
https://instagram.com/assetpicker

💬 AssetPicker 부동산 정보 오픈채팅
https://open.kakao.com/o/giaqO4Ii

#환율 #달러환율 #엔화환율 #유로환율 #금리 #수은채 #채권금리 #시장지표 #경제지표 #MarketReader #AssetPicker
""",
        "tags": [
            "MarketReader",
            "AssetPicker",
            "환율",
            "오늘환율",
            "환율정보",
            "달러환율",
            "원달러환율",
            "USDKRW",
            "엔화환율",
            "원엔환율",
            "JPYKRW",
            "유로환율",
            "원유로환율",
            "EURKRW",
            "금리",
            "오늘금리",
            "채권금리",
            "수은채",
            "수은채금리",
            "수은채유통수익률",
            "한국수출입은행",
            "KEXIM",
            "KEXIM Bond Yield",
            "시장지표",
            "경제지표",
            "금융시장",
            "경제뉴스",
            "경제정보",
            "금융정보",
            "데일리마켓",
            "마켓브리핑",
            "시장전광판",
            "환율전광판",
            "금리전광판",
            "shorts",
            "youtube shorts",
        ],
        "video_path": (
            ROOT
            / "output"
            / "market_reader"
            / "{stamp}"
            / "market_reader_{stamp}.mp4"
        ),
        "playlists": [
            "Market Reader",
        ],
    },
}


def get_credentials() -> Credentials:
    # 1) 로컬: .secrets/youtube_token.json 사용
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES,
        )

    # 2) GitHub Actions: Secrets -> 환경변수 사용
    else:
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

        if not all(
            [
                client_id,
                client_secret,
                refresh_token,
            ]
        ):
            raise RuntimeError(
                "YouTube credentials are missing. "
                "Use .secrets/youtube_token.json locally or set "
                "YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, "
                "YOUTUBE_REFRESH_TOKEN."
            )

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        if TOKEN_FILE.parent.exists() and TOKEN_FILE.exists():
            TOKEN_FILE.write_text(
                credentials.to_json(),
                encoding="utf-8",
            )

    if not credentials.valid:
        raise RuntimeError(
            "YouTube credentials are not valid."
        )

    return credentials


def get_youtube():
    return build(
        "youtube",
        "v3",
        credentials=get_credentials(),
    )


def find_playlist_ids(
    youtube,
    names: list[str],
) -> dict[str, str]:
    wanted = set(names)
    found: dict[str, str] = {}

    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50,
    )

    while request:
        response = request.execute()

        for item in response.get("items", []):
            title = item["snippet"]["title"]

            if title in wanted:
                found[title] = item["id"]

        request = youtube.playlists().list_next(
            request,
            response,
        )

    missing = wanted - set(found)

    if missing:
        raise RuntimeError(
            "YouTube playlist not found: "
            + ", ".join(sorted(missing))
        )

    return found


def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
) -> str:
    if not video_path.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": PRIVACY_STATUS,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print()
    print(f"Uploading: {video_path}")
    print(f"Title: {title}")
    print(f"Privacy requested: {PRIVACY_STATUS}")

    response = None

    while response is None:
        status, response = request.next_chunk()

        if status:
            print(
                f"Upload progress: "
                f"{int(status.progress() * 100)}%"
            )

    video_id = response["id"]

    print(f"Uploaded: {video_id}")
    print(
        f"https://www.youtube.com/watch?v={video_id}"
    )

    return video_id


def add_to_playlists(
    youtube,
    video_id: str,
    playlist_ids: list[str],
) -> None:
    for playlist_id in playlist_ids:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    },
                }
            },
        ).execute()

        print(
            f"Added to playlist: {playlist_id}"
        )


def upload_one(
    youtube,
    kind: str,
    stamp: str,
    display_date: str,
) -> str:
    config = VIDEO_CONFIGS[kind]

    video_path = Path(
        str(config["video_path"]).format(
            stamp=stamp
        )
    )

    title = config["title"].format(
        display_date=display_date
    )

    playlist_names = config["playlists"]

    print()
    print("=" * 60)
    print(f"PROCESSING: {kind}")
    print("=" * 60)
    print(f"Video: {video_path}")

    playlist_map = find_playlist_ids(
        youtube,
        playlist_names,
    )

    video_id = upload_video(
        youtube=youtube,
        video_path=video_path,
        title=title,
        description=config["description"],
        tags=config["tags"],
    )

    upload_captions(
        youtube=youtube,
        video_id=video_id,
        video_path=video_path,
    )

    add_to_playlists(
        youtube,
        video_id,
        [
            playlist_map[name]
            for name in playlist_names
        ],
    )

    print()
    print(f"✅ {kind} complete")

    return video_id


def main():
    now = datetime.now(KST)

    stamp = now.strftime("%Y-%m-%d")
    display_date = now.strftime("%Y.%m.%d")

    youtube = get_youtube()

    print()
    print("=" * 60)
    print(f"YouTube upload: {stamp}")
    print("=" * 60)

    for kind in [
        "ap_daily",
        "development",
        "market_reader",
    ]:
        upload_one(
            youtube,
            kind,
            stamp,
            display_date,
        )

    print()
    print("=" * 60)
    print("ALL YOUTUBE UPLOADS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()