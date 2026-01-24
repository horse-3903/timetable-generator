import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
WEB_DIR = ROOT / "web"
sys.path.append(str(SRC_DIR))

from app.calendar_builder import build_hci_calendar  # noqa: E402
from app.constants import DEFAULT_CALENDAR_NAME, DEFAULT_YEAR  # noqa: E402
from app.logging_util import setup_logging  # noqa: E402

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="HCI Calendar Builder", version="1.0.0")


class BuildRequest(BaseModel):
    year: int = DEFAULT_YEAR
    owner_email: str
    calendar_name: str = DEFAULT_CALENDAR_NAME
    concurrency: int = 4


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/build")
async def build_calendar(req: BuildRequest) -> dict:
    try:
        cal_id = await build_hci_calendar(
            year=req.year,
            owner_email=req.owner_email,
            calendar_name=req.calendar_name,
            concurrency=req.concurrency,
        )
    except Exception as exc:
        logger.exception("Calendar build failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"calendar_id": cal_id}


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
