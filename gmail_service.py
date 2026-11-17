import os
from datetime import datetime, timezone
from email.utils import parseaddr
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import SERVICE_DOMAINS

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def gmail_client():
    required = ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing Gmail OAuth environment variables: " + ", ".join(missing))
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def search_latest_service_email(service_name: str, requested_address: str):
    if service_name not in SERVICE_DOMAINS:
        raise ValueError("Unsupported service.")
    # The entered address is used as a recipient filter; only metadata is read.
    domains = SERVICE_DOMAINS[service_name]
    sender_query = " OR ".join(f"from:{domain}" for domain in domains)
    query = f"to:{requested_address} ({sender_query})"
    client = gmail_client()
    try:
        result = client.users().messages().list(
            userId="me", q=query, maxResults=10
        ).execute()
        messages = result.get("messages", [])
        if not messages:
            return None

        # Gmail returns newest first for this query.
        msg = client.users().messages().get(
            userId="me", id=messages[0]["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()
        headers = {
            h["name"].lower(): h["value"]
            for h in msg.get("payload", {}).get("headers", [])
        }
        sender_name, sender_email = parseaddr(headers.get("from", ""))
        internal_ms = int(msg.get("internalDate", "0"))
        received = datetime.fromtimestamp(internal_ms / 1000, tz=timezone.utc)
        return {
            "from": f"{sender_name} <{sender_email}>" if sender_name else sender_email,
            "subject": headers.get("subject", "(no subject)"),
            "date": received.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
    except HttpError as exc:
        raise RuntimeError(f"Gmail API error: {exc}") from exc
