"""
AI Email Agent
--------------
Uses Claude to draft emails and sends them via Gmail API.

SETUP (one-time):
1. Go to https://console.cloud.google.com
2. Create a project → Enable Gmail API
3. Credentials → OAuth 2.0 Client ID → Desktop App → Download as credentials.json
4. Place credentials.json in the same folder as this script
5. pip install google-auth google-auth-oauthlib google-api-python-client anthropic
6. Set your Anthropic API key as an environment variable:
   Windows: setx ANTHROPIC_API_KEY "your-key-here"
   Then restart your terminal.
"""

import os
import base64
import anthropic
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scope — sending only
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TONES = {
    "1": "professional",
    "2": "casual/friendly",
    "3": "formal",
    "4": "persuasive",
    "5": "concise/brief",
}


# ──────────────────────────────────────────────
# Gmail Auth
# ──────────────────────────────────────────────

def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    if not os.path.exists(creds_path):
        print("\n❌ credentials.json not found in this folder.")
        print("   Follow the setup steps at the top of this script.\n")
        exit(1)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ──────────────────────────────────────────────
# Claude Draft Generation
# ──────────────────────────────────────────────

def draft_email_with_claude(recipient_email, topic, tone, sender_name, sender_role, extra_context):
    """Call Claude API to draft an email."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ANTHROPIC_API_KEY environment variable not set.")
        print("   Run: setx ANTHROPIC_API_KEY \"your-key-here\" and restart terminal.\n")
        exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert email writer. Draft a {tone} email based on the details below.

Sender name: {sender_name}
Sender role/context: {sender_role}
Recipient email: {recipient_email}
Email topic/goal: {topic}
Additional context: {extra_context if extra_context else 'None'}

Return ONLY the email in this exact format — nothing else:
SUBJECT: <subject line here>

<email body here>

Sign off with the sender's name."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()


# ──────────────────────────────────────────────
# Parse Subject + Body from Claude's response
# ──────────────────────────────────────────────

def parse_draft(draft_text):
    """Extract subject and body from Claude's response."""
    lines = draft_text.strip().splitlines()
    subject = ""
    body_lines = []
    found_subject = False

    for i, line in enumerate(lines):
        if line.upper().startswith("SUBJECT:"):
            subject = line[8:].strip()
            found_subject = True
        elif found_subject:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    return subject, body


# ──────────────────────────────────────────────
# Send via Gmail API
# ──────────────────────────────────────────────

def send_email(service, to, subject, body):
    """Send email using Gmail API."""
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print("\n" + "=" * 50)
    print("       AI Email Agent (Powered by Claude)")
    print("=" * 50)

    # Collect inputs
    recipient_email = input("\nRecipient email address: ").strip()
    topic = input("What is the email about / what do you want to accomplish?\n   > ").strip()

    print("\nChoose a tone:")
    for key, val in TONES.items():
        print(f"   {key}. {val.capitalize()}")
    tone_choice = input("   Enter number (1-5): ").strip()
    tone = TONES.get(tone_choice, "professional")

    print("\nA bit about you (to personalize the email):")
    sender_name = input("   Your name: ").strip()
    sender_role = input("   Your role / title / context (e.g. 'CS grad student at RIT'): ").strip()
    extra_context = input("   Any extra context for Claude? (press Enter to skip): ").strip()

    # Draft with Claude
    print("\nDrafting your email with Claude...\n")
    draft = draft_email_with_claude(recipient_email, topic, tone, sender_name, sender_role, extra_context)
    subject, body = parse_draft(draft)

    # Show draft
    print("─" * 50)
    print("DRAFT EMAIL")
    print("─" * 50)
    print(f"To:      {recipient_email}")
    print(f"Subject: {subject}")
    print(f"\n{body}")
    print("─" * 50)

    # Confirm
    choice = input("\nSend this email? (y = send / n = cancel / e = edit subject): ").strip().lower()

    if choice == "e":
        subject = input("New subject line: ").strip()
        choice = input("Send now? (y/n): ").strip().lower()

    if choice == "y":
        print("\nConnecting to Gmail...")
        service = get_gmail_service()
        result = send_email(service, recipient_email, subject, body)
        print(f"\nEmail sent! Message ID: {result['id']}")
    else:
        print("\n❌ Email cancelled. Nothing was sent.")

    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()