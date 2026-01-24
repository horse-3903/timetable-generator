from tqdm import tqdm

from util.google_calendar.api_util import get_service

TIMEZONE = "Asia/Singapore"

def create_calendar(title: str, desc: str = None) -> dict:
    service = get_service()

    info = {
        "summary": title,
        "description": desc,
        "timeZone": TIMEZONE,
    }

    calendar = service.calendars().insert(body=info).execute()

    return calendar

def get_calendar(cal_id: str) -> dict:
    service = get_service()

    cal = service.calendarList().get(calendarId=cal_id).execute()

    return cal

def list_calendar() -> dict:
    service = get_service()

    cal_lst = service.calendarList().list().execute()

    return cal_lst

def update_calendar(cal_id: str, body: dict) -> dict:
    service = get_service()

    cal = service.calendarList().update(
        calendarId=cal_id, 
        body=body
    ).execute()

    return cal

def delete_calendar(cal_id: str) -> None:
    service = get_service()
    
    service.calendars().delete(calendarId=cal_id).execute()

def clear_calendar_list() -> None:
    cal_lst = list_calendar()

    for cal in tqdm(cal_lst["items"]):
        cal_id = cal["id"]
        delete_calendar(cal_id=cal_id)

def list_calendar_events(cal_id: str) -> list:
    service = get_service()
    event_lst = []

    page_token = None
    while True:
        events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        
        event_lst += events["items"]
        page_token = events.get("nextPageToken")
        
        if not page_token:
            break

    return event_lst

def delete_calendar_events(cal_id: str, event_id: str) -> None:
    service = get_service()

    service.events().delete(calendarId=cal_id, eventId=event_id).execute()

def clear_calendar_events(cal_id: str) -> None:
    events = list_calendar_events(cal_id=cal_id)

    for e in tqdm(events):
        delete_calendar_events(cal_id=cal_id, event_id=e["id"])    

if __name__ == "__main__":
    service = get_service()
