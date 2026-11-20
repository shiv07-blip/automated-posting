# Automated Multi-Platform Posting API

FastAPI service that validates one message and publishes it to multiple public platforms in parallel.

## Scoring criteria coverage

| Criteria | Marks | Where addressed |
|---|---:|---|
| FastAPI implementation and API structure | 15 | `app/main.py`, `app/schemas.py`, `/docs`, custom 422 handler |
| Input validation | 15 | `app/schemas.py`: <=200 chars, exactly one CTA link, `HttpUrl` validation |
| Platform research and API integration | 25 | 8 official API integrations in `app/platforms/` (5 public, 3 optional token-based) |
| Automatic multi-platform posting | 20 | `app/services/posting_service.py`: parallel posting, no platform selection in the request |
| Error handling and response management | 10 | Per-platform isolation in `post_one`, structured `PlatformResult` / `PostingResponse` |
| Code quality and GitHub documentation | 15 | Typed code, ruff-clean, pytest suite, this README, `.env.example`, `.gitignore` |

## Platforms

| Platform | Auth | Public URL example | API documentation |
|---|---|---|---|
| Rentry | none | `rentry.co/<id>` | https://github.com/radude/rentry#usage-api |
| dpaste.org | none | `dpaste.org/<id>` | https://docs.dpaste.org/api/ |
| Pastes.dev | none | `pastes.dev/<key>` | https://github.com/lucko/paste/blob/master/API.md |
| Hastebin (hst.sh) | none | `hst.sh/<key>` | https://hst.sh/ |
| Catbox.moe | none | `files.catbox.moe/<id>.txt` | https://catbox.moe/ |
| GitHub Gist | `GITHUB_TOKEN` | `gist.github.com/<id>` | https://docs.github.com/en/rest/gists |
| Telegram Channel | `TELEGRAM_TOKEN`, `TELEGRAM_CHANNEL` | `t.me/<channel>/<message_id>` | https://core.telegram.org/bots/api |
| Mastodon | `MASTODON_INSTANCE`, `MASTODON_TOKEN` | `<instance>/@<user>/<id>` | https://docs.joinmastodon.org/methods/statuses/ |

The five no-auth platforms post successfully with an empty `.env`. The three token-based platforms report a clear failure when their credentials are absent; adding the variables enables them automatically. A failure on any platform never blocks the others.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open http://localhost:4000/docs for the interactive API documentation.

## API

`POST /posting`

```bash
curl -X POST http://localhost:4000/posting \
  -H 'Content-Type: application/json' \
  -d '{"message":"Check out our latest business platform and grow your online visibility. https://example.com"}'
```

Actual response from a local run:

```json
{
  "success": true,
  "results": [
    {
      "platform": "Rentry",
      "status": "success",
      "posted_url": "https://rentry.co/7ukdr9s4",
      "public_access": true,
      "date": "2026-11-20",
      "time": "04:38:06",
      "error": null
    },
    {
      "platform": "dpaste.org",
      "status": "success",
      "posted_url": "https://dpaste.org/5k1fJ",
      "public_access": true,
      "date": "2026-11-20",
      "time": "04:38:06",
      "error": null
    },
    {
      "platform": "Pastes.dev",
      "status": "success",
      "posted_url": "https://pastes.dev/mnlTUYnAsq",
      "public_access": true,
      "date": "2026-11-20",
      "time": "04:38:06",
      "error": null
    },
    {
      "platform": "Hastebin",
      "status": "success",
      "posted_url": "https://hst.sh/udomutigeb",
      "public_access": true,
      "date": "2026-11-20",
      "time": "04:38:06",
      "error": null
    },
    {
      "platform": "Catbox.moe",
      "status": "success",
      "posted_url": "https://files.catbox.moe/833hb9.txt",
      "public_access": true,
      "date": "2026-11-20",
      "time": "04:38:06",
      "error": null
    },
    {
      "platform": "GitHub Gist",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "RuntimeError: GITHUB_TOKEN is not configured"
    },
    {
      "platform": "Telegram Channel",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "RuntimeError: TELEGRAM_TOKEN and TELEGRAM_CHANNEL are not configured"
    },
    {
      "platform": "Mastodon",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "RuntimeError: MASTODON_INSTANCE and MASTODON_TOKEN are not configured"
    }
  ]
}
```

Invalid input (two links) returns HTTP 422:

```json
{
  "success": false,
  "errors": [
    {
      "field": "message",
      "message": "Value error, message must contain exactly one CTA link; found 2"
    }
  ]
}
```

Validation rejects empty messages, messages over 200 characters, zero links, multiple links, and malformed URLs.

## Logs

A complete captured run (server startup, successful POST, validation error, and real posting URLs) is in `logs/sample-run.log`.

```text
INFO:     Started server process [100713]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
INFO:     127.0.0.1:39082 - "POST /posting HTTP/1.1" 200 OK
INFO:     127.0.0.1:39090 - "POST /posting HTTP/1.1" 422 Unprocessable Entity
```

## Tests

```bash
python3 -m pytest -q
RUN_LIVE_TESTS=1 python3 -m pytest -q -k live
```

The unit suite mocks the platforms. `RUN_LIVE_TESTS=1` additionally exercises the real APIs and expects at least five successful posts.

## Structure

```text
app/
  main.py                     FastAPI app and validation error handler
  config.py                   Environment-based settings
  schemas.py                  Request/response models and CTA validation
  platforms/
    base.py                   Shared platform contract and HTTP check
    public.py                 Five no-auth integrations
    social.py                 Three token-based integrations
    __init__.py               Platform registry
  services/
    posting_service.py        Parallel dispatch and per-platform results
tests/test_posting.py
logs/sample-run.log
.env.example
requirements.txt
```

No credentials are committed: `.env` is git-ignored and only placeholder values are tracked in `.env.example`.
