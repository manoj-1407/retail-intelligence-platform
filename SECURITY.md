# Security Policy

## Reporting a Vulnerability

Do not open a public issue for security vulnerabilities. Contact the maintainer directly.

## Credential Situation

Earlier commits contained a placeholder database password in docker-compose.yml.
This was a local development placeholder — not a production credential.
It has been scrubbed from git history via `git filter-repo`.

All secrets are strictly required environment variables. The application validates them
at startup and refuses to run if any are absent or too short.

## Security Controls

| Control | Implementation |
|---|---|
| JWT secret | Required env var, minimum 32 chars enforced by Pydantic validator at startup |
| DB password | Required env var, no default, never logged |
| CORS | Explicit origin list via `CORS_ORIGINS` env var — no wildcard |
| Rate limiting | Per-IP via slowapi — 30–60 req/min per endpoint |
| SQL injection | Parameterized queries only — no f-strings used in SQL text |
| Passwords | bcrypt hashed — never stored or logged as plaintext |
| Distributed locking | Redlock via Redis SET NX PX — prevents race conditions on inventory |
| Timezone handling | All datetimes use `datetime.now(timezone.utc)` — no deprecated `utcnow()` |
| JWT library | PyJWT 2.8.0 — actively maintained, no deprecated datetime internals |
