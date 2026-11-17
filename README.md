# Service Mail Notifier (Telegram)

A standalone Python Telegram bot for an owner and authorized admins. It asks the user to
choose Disney+, Netflix, or ChatGPT first, then asks for a recipient email address and
searches one connected Gmail inbox for the newest matching message.

## Security scope

This starter intentionally reports message metadata only (sender, subject, received time).
It does not read message bodies, extract one-time passwords, or forward login codes.
Use it only with Gmail inboxes and accounts you are authorized to administer.

## Requirements

- Python 3.10+
- A Telegram bot token from BotFather
- A Google Cloud OAuth client configured for the Gmail API
- Gmail OAuth refresh token with `gmail.readonly` scope

## Environment variables

Copy `.env.example` values into your Voroa environment-variable settings. Do not commit
secrets or upload a populated `.env` file to GitHub.

Required:
- `TELEGRAM_BOT_TOKEN`
- `OWNER_TELEGRAM_ID` (numeric Telegram user ID)
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`

## Run locally for testing

```bash
pip install -r requirements.txt
python main.py
```

## Voroa deployment

Create a **new, separate Voroa project/worker** for this bot. Do not reuse the VFinder
project or its environment variables.

- Runtime: Python
- Install/build command: `pip install -r requirements.txt`
- Start command: `python main.py`
- Configure all required environment variables in the Voroa project.
- Enable automatic restart/recovery if Voroa provides that setting.
- If Voroa containers are ephemeral, configure persistent storage for `bot.sqlite3`
  or admin records may be lost when the worker is recreated.
- Keep the worker to one active replica when using Telegram long polling.

Voroa's exact UI and persistence options may vary; verify the platform's current worker
requirements before deploying.

## Telegram commands

- `/start` — choose service, then enter recipient email
- `/addadmin TELEGRAM_USER_ID` — owner only
- `/removeadmin TELEGRAM_USER_ID` — owner only
- `/admins` — owner only

## Gmail search behavior

The bot searches for messages addressed to the supplied email and sent from configured
service domains. Domain filters are in `config.py`; review them against the legitimate
sender domains used by your own service notifications. It returns only metadata.
