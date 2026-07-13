from pathlib import Path
import base64
from datetime import datetime

import resend

from app.config import (
    RESEND_API_KEY,
    FROM_EMAIL,
    TO_EMAIL,
)

from app.exporters.email_template import EMAIL_HTML

today_str = datetime.now().strftime("%Y.%m.%d")

resend.api_key = RESEND_API_KEY


def send_daily_email():
    print("📧 Preparing daily email...")

    today_dirs = sorted(Path("output/daily").iterdir())

    if not today_dirs:
        raise FileNotFoundError("output/daily 폴더에 생성된 결과가 없습니다.")

    today = today_dirs[-1]

    ORDER = [
        ("cover.png", "01_Cover.png"),
        ("introduction.png", "02_Introduction.png"),
        ("issue_1.png", "03_Issue_1.png"),
        ("issue_2.png", "04_Issue_2.png"),
        ("issue_3.png", "05_Issue_3.png"),
        ("issue_4.png", "06_Issue_4.png"),
        ("issue_5.png", "07_Issue_5.png"),
        ("insight.png", "08_Insight.png"),
        ("ending.png", "09_Ending.png"),
    ]

    attachments = []

    for original, filename in ORDER:
        image = today / original

        if not image.exists():
            print(f"⚠️ Missing: {image}")
            continue

        with open(image, "rb") as f:
            attachments.append(
                {
                    "filename": filename,
                    "content": base64.b64encode(
                        f.read()
                    ).decode("utf-8"),
                }
            )

    print(f"📎 Attachments: {len(attachments)}")

    try:
        response = resend.Emails.send(
            {
                "from": FROM_EMAIL,
                "to": TO_EMAIL,
                "subject": f"🏠 AP Daily | {today_str}",
                "html": EMAIL_HTML,
                "attachments": attachments,
            }
        )

        print("✅ Daily email sent.")
        print(response)

        return response

    except Exception as e:
        print("❌ Failed to send email.")
        print(e)
        raise