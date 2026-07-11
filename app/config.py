import os

from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("FROM_EMAIL")

TO_EMAIL = os.getenv("TO_EMAIL")

SERPER_API_KEY = os.getenv("SERPER_API_KEY")