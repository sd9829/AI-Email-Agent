# AI Email Agent

Drafts and sends emails from your Gmail account using Claude. You provide a recipient, topic, and tone — the agent writes the email and sends it after your approval.

---

## Requirements

- Python 3.8+
- A Gmail account
- An Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

---

## One-Time Setup

### 1. Install dependencies
```bash
pip install google-auth google-auth-oauthlib google-api-python-client anthropic
```

### 2. Set your Anthropic API key
```bash
# Windows
setx ANTHROPIC_API_KEY "your-key-here"
```
Restart your terminal after running this.

### 3. Enable Gmail API
1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project
2. Search for **Gmail API** and enable it
3. Go to **Credentials → Create Credentials → OAuth 2.0 Client ID**
4. Set application type to **Desktop App** and click Create
5. Download the credentials file and rename it to `credentials.json`
6. Place `credentials.json` in the same folder as `email_agent.py`

---

## Usage

```bash
python email_agent.py
```

On first run, a browser window will open asking you to log in to Google and grant permission. This only happens once — a `token.json` file is saved for future runs.

The agent will prompt you for:
- Recipient email address
- What the email is about / your goal
- Tone (professional, casual, formal, persuasive, or concise)
- Your name and role (used to personalize the email)
- Any extra context (optional)

It will then show you the full draft. You can:
- `y` — send it
- `n` — cancel
- `e` — edit the subject line before sending

---

## Files

| File | Description |
|---|---|
| `email_agent.py` | Main script |
| `credentials.json` | Your Google OAuth credentials (you provide this) |
| `token.json` | Auto-generated after first login, do not delete |

---

## Notes

- `credentials.json` and `token.json` are sensitive — do not commit them to GitHub. Add them to your `.gitignore`.
- The agent only has permission to **send** email, not read or modify your inbox.

