# Security Policy

We take the security of this project seriously. Please follow these guidelines:

- Report vulnerabilities privately via email or your team’s preferred channel. Do not open public issues for security reports.
- Never commit secrets. Use `.env` locally; keep `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `GMAIL_CLIENT_SECRET`, etc. out of version control.
- Use `.env.example` as the source of truth for required configuration keys. Add new keys there with safe placeholders.
- Rotate any leaked credentials immediately and invalidate exposed tokens.
- Avoid writing sensitive data to the repo. Runtime data should live under `data/`, which is gitignored by default.

If you are unsure whether something constitutes a security issue, err on the side of reporting privately.
