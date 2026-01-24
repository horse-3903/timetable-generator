from util.google_calendar.calendar_util import list_calendar, list_calendar_events

# api tests

# acl tests

# calendar tests

# event tests

# db tests

if __name__ == "__main__":
    odd_cal = list_calendar()["items"][0]
    odd_events = list_calendar_events(cal_id=odd_cal["id"])
    print(odd_events[0])
