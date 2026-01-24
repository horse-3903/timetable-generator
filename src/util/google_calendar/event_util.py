from datetime import datetime

from googleapiclient.discovery import Resource

from util.google_calendar.api_util import get_service

BATCH_LIMIT = 100
TIMEZONE = "Asia/Singapore"

def config_recurrence() -> str:
    # found in https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.5.3
    pass

def create_event(
    cal_id: str,
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    location: str = None,
    desc: str = None,
    recurrence: list = None,
    emails: list = None,
    colour: str = None,
    service: Resource = None,
) -> dict:
    service = service or get_service()

    info = {
        "summary": title,
        "start": {
            "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        },
    }
    
    if location:
        info["location"] = location
    
    if desc:
        info["description"] = desc
    
    if recurrence:
        info["recurrence"] = recurrence
    
    if emails:
        info["attendees"] = [{"email": e} for e in emails]

    if colour:
        info["colorId"] = colour

    event = service.events().insert(calendarId=cal_id, body=info).execute()

    return event

def update_event(
    cal_id: str,
    event_id: str,
    title: str = None,
    start_dt: datetime = None,
    end_dt: datetime = None,
    location: str = None,
    desc: str = None,
    recurrence: list = None,
    emails: list = None,
    colour: str = None,
    service: Resource = None,
) -> dict:
    service = service or get_service()

    info = service.events().get(calendarId=cal_id, eventId=event_id).execute()
    
    if title:
        info["summary"] = title

    if start_dt:
        info["start"] = {
            "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        }

    if end_dt:
        info["end"] = {
            "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        }
    
    if location:
        info["location"] = location
    
    if desc:
        info["description"] = desc
    
    if recurrence:
        info["recurrence"] = recurrence
    
    if emails:
        info["attendees"] = [{"email": e} for e in emails]

    if colour:
        info["colorId"] = colour

    event = service.events().update(calendarId=cal_id, eventId=event_id, body=info).execute()

    return event

def build_event_payload(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    location: str = None,
    desc: str = None,
    recurrence: list = None,
    emails: list = None,
    colour: str = None,
) -> dict:
    info = {
        "summary": title,
        "start": {
            "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": TIMEZONE,
        },
    }

    if location:
        info["location"] = location

    if desc:
        info["description"] = desc

    if recurrence:
        info["recurrence"] = recurrence

    if emails:
        info["attendees"] = [{"email": e} for e in emails]

    if colour:
        info["colorId"] = colour

    return info

def batch_create_events(
    cal_id: str,
    payloads: list[dict],
    service: Resource = None,
    batch_limit: int = BATCH_LIMIT,
) -> None:
    service = service or get_service()
    for i in range(0, len(payloads), batch_limit):
        batch = service.new_batch_http_request()
        for payload in payloads[i:i + batch_limit]:
            req = service.events().insert(calendarId=cal_id, body=payload)
            batch.add(req)
        batch.execute()
