import asyncio
import logging
import re
from datetime import timedelta

from tqdm import tqdm

from util.db.db_util import clump_data, fetch_data, format_data, get_subjects
from util.google_calendar.acl_util import insert_acl
from util.google_calendar.calendar_util import clear_calendar_list, create_calendar
from util.google_calendar.event_util import create_event
from util.isp.acad_calendar_util import get_acad_calendar
from util.isp.event_calendar_util import get_event_calendar_batch

logger = logging.getLogger(__name__)


async def save_timetable(_class: str, email: str):
    db_data = fetch_data(_class=_class)

    even_data = [d for d in db_data if "Even" in d[0]]
    odd_data = [d for d in db_data if d not in even_data]

    acad_data = await get_acad_calendar(year=2024, term=2)
    acad_data = acad_data.items()

    odd_dates, even_dates = list(acad_data)[:2]
    odd_week, (odd_start, odd_end) = odd_dates
    even_week, (even_start, even_end) = even_dates

    odd_data = format_data(data=odd_data, start_dt=odd_start)
    even_data = format_data(data=even_data, start_dt=even_start)

    odd_data = clump_data(data=odd_data)
    even_data = clump_data(data=even_data)

    all_subj_lst = get_subjects(data=odd_data + even_data)
    all_subj_lst = sorted(all_subj_lst, key=len)

    non_subj_lst = ["ACAD CONS", "PACE"]
    subj_lst = [
        s
        for s in all_subj_lst
        if ("".join(re.findall("[A-Za-z]", s)).isupper() or "HBL" in s)
        and s not in non_subj_lst
    ]
    break_lst = ["Recess", "Lunch"]

    odd_cal = create_calendar(title="2024 4A3 T2 (Odd)")
    even_cal = create_calendar(title="2024 4A3 T2 (Even)")

    insert_acl(cal_id=odd_cal["id"], scope="user", email=email, role="owner")
    insert_acl(cal_id=even_cal["id"], scope="user", email=email, role="owner")

    for d in tqdm(odd_data):
        if d["title"] in subj_lst:
            colour = "9"
        elif d["title"] in break_lst:
            colour = "10"
        else:
            colour = "3"

        create_event(
            cal_id=odd_cal["id"],
            title=d["title"],
            start_dt=d["start"],
            end_dt=d["end"],
            colour=colour,
            recurrence=["RRULE:FREQ=WEEKLY;INTERVAL=2;COUNT=5"],
        )

    for d in tqdm(even_data):
        if d["title"] in subj_lst:
            colour = "9"
        elif d["title"] in break_lst:
            colour = "1"
        else:
            colour = "8"

        create_event(
            cal_id=even_cal["id"],
            title=d["title"],
            start_dt=d["start"],
            end_dt=d["end"],
            colour=colour,
            recurrence=["RRULE:FREQ=WEEKLY;INTERVAL=2;COUNT=5"],
        )

    return odd_cal, even_cal


async def save_weeks(email: str):
    acad_data = await get_acad_calendar(year=2024, term=2)
    acad_data = acad_data.items()

    week_cal = create_calendar(title="2024 T2 Week Calendar")
    insert_acl(cal_id=week_cal["id"], scope="user", email=email, role="owner")

    for week, (start, end) in tqdm(acad_data):
        end += timedelta(hours=23, minutes=59)
        create_event(cal_id=week_cal["id"], title=week, start_dt=start, end_dt=end)


async def save_events(email: str):
    events_by_month = await get_event_calendar_batch(2024, list(range(1, 13)))
    events_lst = [event for month in events_by_month.values() for event in month]

    events_cal = create_calendar(title="2024 HCI Events Calendar")
    insert_acl(cal_id=events_cal["id"], scope="user", email=email, role="owner")

    for e in tqdm(events_lst):
        desc = (
            f"In Charge: {e['in_charge']}\n"
            f"Venue: {e['venue']}\n"
            f"Details: {e['details']}\n"
        )
        create_event(
            cal_id=events_cal["id"],
            title=e["title"],
            start_dt=e["start_dt"],
            end_dt=e["end_dt"],
            desc=desc,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    clear_calendar_list()
    # asyncio.run(save_timetable(_class="4A3", email="chongchoonhourafael@gmail.com"))
    # asyncio.run(save_weeks(email="chongchoonhourafael@gmail.com"))
    asyncio.run(save_events(email="chongchoonhourafael@gmail.com"))
    
