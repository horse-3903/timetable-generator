# timetable-generator

Generate a complete HCI academic + ISP events calendar in Google Calendar.
Includes a CLI, an API server, and a SaaS-style frontend.

## Features
- Builds a single calendar with academic weeks + ISP events for 2026
- Labels weeks as "Term x Week y"
- Applies a blue/purple event palette
- Shares calendar ownership with a target email
- Batch inserts for faster creation

## Project structure
```
src/
  app/                    # orchestration + configuration
  util/                   # ISP + Google Calendar helpers
server/                   # FastAPI server
web/                      # SaaS frontend
secrets/                  # credentials + cookies (not committed)
```

## Requirements
- Python 3.10+
- Playwright (Chromium)
- Google service account credentials
- ISP cookies JSON

## Setup
1) Create a virtual environment and install dependencies:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

2) Add secrets:
```
secrets/
  cookies.json
  service-credentials.json
```

### `secrets/cookies.json`
Export cookies from the ISP site and save them as a JSON list.

### `secrets/service-credentials.json`
Create a Google Cloud service account with Calendar API enabled, download the JSON,
and save it as `secrets/service-credentials.json`.

Important: share the created calendar with the service account email if using a
personal Google account, or configure domain-wide delegation for Workspace.

## CLI usage
```bash
python -u src/main.py --owner-email you@domain.com
```

Optional flags:
- `--year` (default: 2026)
- `--calendar-name` (default: "HCI 2026 Calendar")
- `--concurrency` (default: 4)

## Server usage
```bash
uvicorn server.main:app --reload
```

API endpoint:
```
POST /api/build
{
  "year": 2026,
  "owner_email": "you@domain.com",
  "calendar_name": "HCI 2026 Calendar",
  "concurrency": 4
}
```

## Frontend usage
Start the server, then open:
```
http://127.0.0.1:8000/
```

## Troubleshooting
- Missing `service-credentials.json` will raise an error in `src/util/google_calendar/api_util.py`.
- Missing or invalid `cookies.json` will stop ISP fetches.
- If Playwright errors, re-run `python -m playwright install`.
