# Gmail OAuth Setup

Follow these steps to enable Gmail/Workspace sending and polling without committing secrets.

1. Create a Google Cloud project and enable the **Gmail API**.
2. Configure an OAuth 2.0 Client ID (Desktop or Web). For Web, allow `http://localhost:8000/oauth` or a similar local callback.
3. Capture the credentials and export them locally (never commit):
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_REDIRECT_URI` (default: `http://localhost:8000/oauth`)
   - `GMAIL_TOKEN_PATH` (default: `.cache/gmail_token.json`)
4. Run the local consent flow to obtain refreshable tokens:
   ```bash
   python3 - <<'PY'
   import os
   from pathlib import Path
   from src.integrations.gmail_auth import GmailAuth, TokenStore

   client_id = os.environ["GMAIL_CLIENT_ID"]
   client_secret = os.environ["GMAIL_CLIENT_SECRET"]
   redirect_uri = os.environ.get("GMAIL_REDIRECT_URI", "http://localhost:8000/oauth")
   token_path = Path(os.environ.get("GMAIL_TOKEN_PATH", ".cache/gmail_token.json"))
   auth = GmailAuth(client_id, client_secret, redirect_uri, TokenStore(token_path))
   url = auth.build_auth_url(["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"])
   print("Authorize via:", url)
   PY
   ```
5. Paste the authorization code into a follow-up exchange to write an offline token to disk:
   ```bash
   python3 - <<'PY'
   import os
   from pathlib import Path
   from src.integrations.gmail_auth import GmailAuth, TokenStore

   code = input("Enter OAuth code: ").strip()
   auth = GmailAuth(
       os.environ["GMAIL_CLIENT_ID"],
       os.environ["GMAIL_CLIENT_SECRET"],
       os.environ.get("GMAIL_REDIRECT_URI", "http://localhost:8000/oauth"),
       TokenStore(Path(os.environ.get("GMAIL_TOKEN_PATH", ".cache/gmail_token.json"))),
   )
   auth.exchange_code(code)
   print("Token saved for offline use.")
   PY
   ```
6. Tokens are stored locally and refreshed automatically; keep the token file out of version control.

Notes:
- The sender uses `List-Unsubscribe` headers when you pass an unsubscribe URL.
- Add test users in the Google Console if the app is in testing mode.
- Never paste access tokens or codes into tracked files.
