import logging
import re
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from util.google_calendar.acl_util import insert_acl
from util.google_calendar.api_util import get_service
from util.google_calendar.calendar_util import create_calendar
from util.google_calendar.event_util import (
    batch_create_events,
    build_event_payload,
)
from util.isp.acad_calendar_util import get_acad_calendar
from util.isp.event_calendar_util import get_event_calendar_batch

from app.constants import (
    DEFAULT_CALENDAR_DESC,
    DEFAULT_CALENDAR_NAME,
    EVENT_COLOUR,
    TERM_COLOURS,
)

logger = logging.getLogger(__name__)

WeekRange = Tuple[datetime, datetime]
AcadCalendar = Dict[str, Dict[str, WeekRange]]


def format_week_title(term: int, week_label: str) -> str:
    match = re.search(r"(\d+)", week_label)
    week_value = match.group(1) if match else week_label.strip()
    return f"Term {term} Week {week_value}"


async def fetch_acad_calendar(year: int) -> AcadCalendar:
    acad_cal: AcadCalendar = {}
    for term in range(4):
        logger.info("Fetching academic calendar for term %s", term + 1)
        acad_cal[f"Term {term + 1}"] = await get_acad_calendar(year, term + 1)
    return acad_cal


def build_acad_payloads(acad_cal: AcadCalendar) -> List[dict]:
    payloads: List[dict] = []
    for term_label, weeks in acad_cal.items():
        term_num = int(term_label.split()[-1])
        colour_id = TERM_COLOURS.get(term_num, "1")

        for week_label, (start_dt, end_dt) in weeks.items():
            title = format_week_title(term_num, week_label)
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            payloads.append(
                build_event_payload(
                    title,
                    start_dt,
                    end_dt,
                    colour=colour_id,
                )
            )
    return payloads


def build_event_payloads(event_cal: Dict[int, Iterable[dict]]) -> List[dict]:
    payloads: List[dict] = []
    for month, month_events in event_cal.items():
        logger.info("Preparing %s events for month %s", len(month_events), month)
        for event in month_events:
            title = event["title"]
            start_dt = event["start_dt"]
            end_dt = event["end_dt"]
            location = event.get("venue")

            desc_parts = []
            in_charge = event.get("in_charge")
            details = event.get("details")
            if in_charge:
                desc_parts.append(f"In charge: {in_charge}")
            if details:
                desc_parts.append(details)
            desc = "\n".join(desc_parts) if desc_parts else None

            payloads.append(
                build_event_payload(
                    title,
                    start_dt,
                    end_dt,
                    location=location,
                    desc=desc,
                    colour=EVENT_COLOUR,
                )
            )
    return payloads


async def build_hci_calendar(
    year: int,
    owner_email: str,
    calendar_name: str = DEFAULT_CALENDAR_NAME,
    calendar_desc: str = DEFAULT_CALENDAR_DESC,
    concurrency: int = 4,
) -> str:
    logger.info("Building HCI calendar for %s", year)
    acad_cal = await fetch_acad_calendar(year)
    event_cal = await get_event_calendar_batch(year, list(range(1, 13)), concurrency=concurrency)

    calendar = create_calendar(calendar_name, desc=calendar_desc)
    cal_id = calendar["id"]
    insert_acl(cal_id, "user", owner_email, "owner")
    logger.info("Created calendar %s and shared ownership with %s", cal_id, owner_email)

    payloads = build_acad_payloads(acad_cal)
    payloads.extend(build_event_payloads(event_cal))

    logger.info("Batch inserting %s events", len(payloads))
    service = get_service()
    batch_create_events(cal_id, payloads, service=service)

    return cal_id
