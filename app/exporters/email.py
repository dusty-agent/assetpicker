from pathlib import Path
import base64
import resend
from app.exporters.email_template import (
    EMAIL_HTML,
)
from datetime import datetime

today_str = datetime.now().strftime("%Y.%m.%d")

from app.config import (
    RESEND_API_KEY,
    FROM_EMAIL,
    TO_EMAIL,
)

resend.api_key = RESEND_API_KEY


def send_daily_email():

    today = Path("output/daily").iterdir()
    today = sorted(today)[-1]

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

    resend.Emails.send(
    {
        "from": FROM_EMAIL,
        "to": TO_EMAIL,
        "subject": f"🏠 AP Daily | {today_str}",
        "html": EMAIL_HTML,
        "attachments": attachments,
    }
)

print("📧 Daily email sent.")