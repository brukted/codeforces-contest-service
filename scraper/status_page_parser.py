from bs4 import BeautifulSoup, Tag
import datetime

import pytz
from models.domain.submission import Submission


def get_status_page_count(page: str) -> int:
    soup = BeautifulSoup(page, "html.parser")
    page_indices = soup.find_all("span", class_="page-index")
    if len(page_indices) == 0:
        return 1
    pages = max(map(lambda x: int(x.string), page_indices))
    return pages


def parse_status_page(page: str) -> list[Submission]:
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table", class_="status-frame-datatable")
    if table is None:
        raise RuntimeError("Can't find submissions table")

    submissions: list[Submission] = []
    rows: list[Tag] = table.find_all("tr", recursive=True)

    # column order: submission id, when, who, problem, lang, verdict, time, memory
    # first row is header
    for row in rows[1:]:
        cells: list[Tag] = row.find_all("td", recursive=False)
        print(cells[0])
        submission_id = int(cells[0].text.strip())
        when = datetime.datetime.strptime(cells[1].text.strip(), "%b/%d/%Y %H:%M")
        # convert when from machine timezone to UTC
        when = datetime.datetime.utcfromtimestamp(when.timestamp())
        # Convert the datetime object to UTC timezone
        utc_timezone = pytz.timezone("UTC")
        when_utc = when.astimezone(utc_timezone)
        who = cells[2].find("a")["href"].split("/")[-1].strip().lower()
        is_virtual = cells[2].find("sup") is not None
        index = cells[3].find("a")["href"].split("/")[-1].strip()
        lang = cells[4].text.strip()
        verdict = cells[5].text.strip()
        time = int("".join(filter(lambda ch: ch.isdigit(), cells[6].text.strip())))
        memory = int("".join(filter(lambda ch: ch.isdigit(), cells[7].text.strip())))
        submissions.append(
            Submission(
                id=submission_id,
                submission_time_utc=datetime.datetime.timestamp(when_utc),
                handle=who,
                is_virtual=is_virtual,
                problem_index=index,
                language=lang,
                verdict=verdict,
                time=time,
                memory=memory,
            )
        )
    return submissions
