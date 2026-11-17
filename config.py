import os

OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Restrict sender searches to known service domains. Review/update these if
# the official sender addresses change. This app reports email metadata only.
SERVICE_DOMAINS = {
    "Disney+": ["disneyplus.com", "disney.com"],
    "Netflix": ["netflix.com"],
    "ChatGPT": ["openai.com"],
}
