from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


ROOT = Path(__file__).resolve().parent

CLIENT_SECRET_FILE = (
    ROOT
    / ".secrets"
    / "youtube_client_secret.json"
)

TOKEN_FILE = (
    ROOT
    / ".secrets"
    / "youtube_token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def main():
    if not CLIENT_SECRET_FILE.exists():
        raise FileNotFoundError(
            f"OAuth client file not found: {CLIENT_SECRET_FILE}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        SCOPES,
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("YouTube OAuth authentication complete")
    print("=" * 60)
    print()
    print(f"Token saved to: {TOKEN_FILE}")
    print()
    print("Do NOT commit this file.")
    print()


if __name__ == "__main__":
    main()