from util.google_calendar.api_util import get_service

def list_calendar_colour() -> dict:
    service = get_service()

    colours = service.colors().get().execute()

    return colours["calendar"]

def list_event_colour() -> dict:
    service = get_service()

    colours = service.colors().get().execute()

    return colours["event"]

# colours
# 1 : pastel blue
# 2 : pastel green
# 3 : purple/violet
# 4 : salmon pastel orange
# 5 : yellow
# 6 : orange
# 7 : sky blue
# 8 : gray
# 9 : dark blue
# 10 : dark green
# 11 : red

colour_combinations = [
    (9, 1, 8),
    (9, 10, 3),
]
