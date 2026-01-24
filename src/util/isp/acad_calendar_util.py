import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from util.isp.isp_util import get_cookies

cal_url = "https://isp.hci.edu.sg/curriculum/acadcalendar.asp"
logger = logging.getLogger(__name__)
_OPTIONS_CACHE: Dict[str, Tuple[dict, dict]] = {}

def fetch_content(session: requests.Session, url: str, cookies: dict) -> str:
    return session.get(url=url, cookies=cookies).text


async def get_soup(url: str, session: requests.Session, cookies: dict):
    content = await asyncio.to_thread(fetch_content, session, url, cookies)

    soup = BeautifulSoup(content, features="html.parser")

    return soup

async def get_options(target_year: Optional[str] = None):
    cache_key = target_year or "__all__"
    if cache_key in _OPTIONS_CACHE:
        return _OPTIONS_CACHE[cache_key]

    cookie_data = await get_cookies()
    if not cookie_data:
        raise ValueError("No cookies found; check secrets/cookies.json")
    cookies = {d["name"]: d["value"] for d in cookie_data}

    with requests.Session() as session:
        logger.info("Fetching academic calendar year options")
        soup = await get_soup(url=cal_url, session=session, cookies=cookies)

        year = soup.find("select", attrs={"name": "year"})
        year_options = [*year.find_all("option")]
        year_options = {e.get_text(): e.attrs["value"] for e in year_options}

        year_to_term_options = {}
        year_values = year_options.values()
        if target_year:
            year_values = [target_year]

        for value in year_values:
            params = {
                "year": value,
            }

            logger.info("Fetching term options for year %s", value)
            soup = await get_soup(
                url=cal_url + "?" + urlencode(params),
                session=session,
                cookies=cookies,
            )

            term = soup.find("select", attrs={"name": "Term"})
            term_options = [*term.find_all("option")]
            term_options = term_options[1:]
            term_options = {e.get_text(): e.attrs["value"] for e in term_options}

            year_to_term_options[value] = term_options

    _OPTIONS_CACHE[cache_key] = (year_options, year_to_term_options)
    return year_options, year_to_term_options

async def get_acad_calendar(year: int, term: int) -> Dict[str, Tuple[datetime, datetime]]:
    year_str = str(year)
    year_options, year_to_term_options = await get_options(target_year=year_str)

    if term not in range(1, 5):
        raise ValueError(f"Invalid Term provided : {term}")

    term = str(term)

    if year_str not in year_options.values():
        raise ValueError(f"Invalid Year provided : {year_str}")
    
    term_options = year_to_term_options[year_str]
    
    params = {
        "year": year_str,
        "term": term_options[f"Term {term}"],
    }

    cookie_data = await get_cookies()
    if not cookie_data:
        raise ValueError("No cookies found; check secrets/cookies.json")
    cookies = {d["name"]: d["value"] for d in cookie_data}

    with requests.Session() as session:
        logger.info("Fetching academic calendar for year %s term %s", year_str, term)
        soup = await get_soup(
            url=cal_url + "?" + urlencode(params),
            session=session,
            cookies=cookies,
        )

    table = soup.find("tr", attrs={"class": "t"}).parent
    rows = [*table.find_all("tr")]
    rows = rows[1:]
    
    week_to_date = {}

    for row in rows:
        data = row.find_all("td")
        week, start_d, end_d, hol = [d.get_text() for d in data]

        start_d = start_d.split()[0]
        end_d = end_d.split()[0]

        start_d = datetime.strptime(start_d, "%d/%m/%Y")
        end_d = datetime.strptime(end_d, "%d/%m/%Y")

        week_to_date[week] = (start_d, end_d)

    return week_to_date

if __name__ == "__main__":
    print(asyncio.run(get_acad_calendar(2024, 3)))
