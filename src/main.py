import argparse
import asyncio
import logging

from app.calendar_builder import build_hci_calendar
from app.constants import DEFAULT_CALENDAR_NAME, DEFAULT_YEAR
from app.logging_util import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the HCI calendar in Google Calendar.")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, help="Year to generate.")
    parser.add_argument(
        "--owner-email",
        default="chongchoonhourafael@gmail.com",
        help="Email to grant calendar ownership.",
    )
    parser.add_argument(
        "--calendar-name",
        default=DEFAULT_CALENDAR_NAME,
        help="Calendar name to create.",
    )
    parser.add_argument("--concurrency", type=int, default=4, help="Playwright page concurrency.")
    return parser.parse_args()


async def main() -> None:
    setup_logging()
    logging.getLogger(__name__).info("Starting calendar build")

    args = parse_args()
    await build_hci_calendar(
        year=args.year,
        owner_email=args.owner_email,
        calendar_name=args.calendar_name,
        concurrency=args.concurrency,
    )


if __name__ == "__main__":
    asyncio.run(main())
