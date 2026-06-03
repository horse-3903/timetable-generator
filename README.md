<div align="center">

# Timetable Generator

Automated academic calendar builder with Google Calendar integration for HCI timetables

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Calendar](https://img.shields.io/badge/Google%20Calendar-4285F4?style=flat-square&logo=googlecalendar&logoColor=white)](https://developers.google.com/calendar)
[![License](https://img.shields.io/github/license/horse-3903/timetable-generator?style=flat-square)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/horse-3903/timetable-generator?style=flat-square)](../../commits)

</div>

---

## Overview

Timetable Generator automates the creation of a complete HCI academic and ISP events calendar in Google Calendar. Given a target year, it scrapes ISP event data, labels academic weeks (e.g., "Term 1 Week 3"), applies a consistent colour palette, and batch-inserts all events via the Google Calendar API. The project exposes a CLI, a FastAPI server, and a SaaS-style web frontend.

---

## Features

- **Full Academic Calendar Generation** — Builds term weeks and ISP events for a given year in a single run
- **Automatic Week Labelling** — Labels each week as "Term x Week y" for easy navigation
- **Consistent Colour Palette** — Applies a blue/purple event theme across all calendar entries
- **Google Calendar Sharing** — Automatically shares calendar ownership with a target email
- **Batch Insertion** — Uses batch API calls for fast calendar population
- **Multiple Interfaces** — CLI, FastAPI REST API, and a web frontend

---

## Tech Stack

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Google Calendar API](https://img.shields.io/badge/Google%20Calendar%20API-4285F4?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://developers.google.com/calendar)

---

## Getting Started

### Prerequisites

- Python 3.10+
- A Google Cloud service account with the **Google Calendar API** enabled
- ISP site cookies (exported as JSON)

### Installation

1. Clone the repository and set up a virtual environment:
   ```bash
   git clone https://github.com/horse-3903/timetable-generator.git
   cd timetable-generator
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m playwright install
   ```

2. Add secrets to the `secrets/` directory (this folder is not committed):

   ```
   secrets/
     cookies.json               # ISP site cookies
     service-credentials.json   # Google service account key
   ```

### Configuring Google Calendar API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the **Google Calendar API** under *APIs & Services → Library*.
4. Create a **Service Account** under *APIs & Services → Credentials*.
5. Download the service account JSON key and save it as `secrets/service-credentials.json`.
6. **Share access**: In Google Calendar, share your target calendar with the service account email address (found in the JSON under `client_email`), granting it *Make changes to events* permission. For Google Workspace, configure domain-wide delegation instead.

### Usage

**CLI:**
```bash
python -u src/main.py --owner-email you@domain.com
```

Optional flags:
| Flag | Default | Description |
|---|---|---|
| `--year` | `2026` | Academic year to generate |
| `--calendar-name` | `"HCI 2026 Calendar"` | Name of the created calendar |
| `--concurrency` | `4` | Number of concurrent API workers |

**API Server:**
```bash
uvicorn server.main:app --reload
```

Send a POST request:
```json
POST /api/build
{
  "year": 2026,
  "owner_email": "you@domain.com",
  "calendar_name": "HCI 2026 Calendar",
  "concurrency": 4
}
```

**Web Frontend:**

Start the server, then open `http://127.0.0.1:8000/` in your browser.

---

## Project Structure

```
timetable-generator/
├── src/
│   ├── app/                # Orchestration and configuration
│   ├── util/               # ISP scraping + Google Calendar helpers
│   └── main.py             # CLI entry point
├── server/
│   └── main.py             # FastAPI server
├── web/                    # SaaS-style frontend
├── secrets/                # Credentials (not committed)
└── requirements.txt
```

---

## Troubleshooting

| Issue | Resolution |
|---|---|
| `service-credentials.json` not found | Ensure the file exists at `secrets/service-credentials.json` |
| ISP fetch fails | Check that `secrets/cookies.json` contains valid, unexpired cookies |
| Playwright errors | Re-run `python -m playwright install` to reinstall browsers |

---

## License

This project is licensed under the [MIT License](LICENSE).
