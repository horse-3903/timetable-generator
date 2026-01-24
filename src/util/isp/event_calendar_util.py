import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from playwright.async_api import async_playwright
from urllib.parse import urlencode

from util.isp.isp_util import get_cookies

cal_url = "https://isp.hci.edu.sg/eventcalendar.asp"
logger = logging.getLogger(__name__)

async def get_playwright(url: str):
    cookies = await get_cookies()
    if not cookies:
        raise ValueError("No cookies found; check secrets/cookies.json")

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()

    await context.add_cookies(cookies=cookies)

    page = await context.new_page()
    await page.goto(url=url)

    await page.wait_for_load_state("domcontentloaded")

    return p, browser, context, page

async def get_event_calendar(year: int, month: int) -> List[dict]:
    if month not in range(1, 13):
        raise ValueError(f"Invalid Month provided : {month}")

    year_str = str(year)
    month_str = str(month)
    
    params = {
        "year": year_str,
        "month": month_str,
    }

    p, browser, context, page = await get_playwright(url=cal_url + "?" + urlencode(params))

    events_lst = await parse_calendar_page(page, year_str)

    await context.close()
    await browser.close()
    await p.stop()

    return events_lst

async def parse_calendar_page(page, year: str) -> List[dict]:
    await page.wait_for_selector("#calendar > div")

    table = page.locator("#calendar > div > div > div")
    events = await table.locator("div").all()

    events_lst = []

    for e in events:
        await e.hover()

        table = page.locator("#calendar > div > div > div")

        info = table.locator("div").last
        values = (await info.inner_text()).splitlines()

        values.pop(1)
        
        keys = ["title", "start_dt", "end_dt", "in_charge", "venue", "details"]
        values = [i.split(": ")[-1] if i[-1:] != ":" else None for i in values]

        dt = values[1]
        
        if "From" in dt:
            dt = dt.split("From ")[-1]
            start_dt, end_dt = [datetime.strptime(d, "%d %b %Y %H:%M") for d in dt.split(" To ")]
        else:
            date = dt.split()[:3]
            date = " ".join(date)
            
            start_dt = end_dt = datetime.strptime(date, "%d %b %Y")
            end_dt = datetime(year=end_dt.year, month=end_dt.month, day=end_dt.day, hour=23, minute=59, second=59)

        values.pop(1)
        values.insert(1, end_dt)
        values.insert(1, start_dt)

        event_details = dict(zip(keys, values))

        events_lst.append(event_details)

    logger.info("Parsed %s events for year %s", len(events_lst), year)
    return events_lst

async def get_event_calendar_batch(year: int, months: List[int], concurrency: int = 3) -> Dict[int, List[dict]]:
    for month in months:
        if month not in range(1, 13):
            raise ValueError(f"Invalid Month provided : {month}")

    cookies = await get_cookies()
    if not cookies:
        raise ValueError("No cookies found; check secrets/cookies.json")

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()
    await context.add_cookies(cookies=cookies)

    semaphore = asyncio.Semaphore(max(1, concurrency))
    results: Dict[int, List[dict]] = {}

    async def fetch_month(month: int) -> None:
        async with semaphore:
            params = {"year": str(year), "month": str(month)}
            url = cal_url + "?" + urlencode(params)
            logger.info("Fetching ISP event calendar: %s", url)
            page = await context.new_page()
            try:
                await page.goto(url=url)
                results[month] = await parse_calendar_page(page, str(year))
            finally:
                await page.close()

    await asyncio.gather(*(fetch_month(month) for month in months))

    await context.close()
    await browser.close()
    await p.stop()

    return results

async def main():
    print(await get_event_calendar(2024, 6))

if __name__ == "__main__":
    asyncio.run(main())
