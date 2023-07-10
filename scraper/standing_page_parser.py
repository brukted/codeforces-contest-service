import datetime
from bs4 import BeautifulSoup

from models.domain.problem_result import ProblemResult
from models.domain.standing import ParticipationType, Standing


def get_submission_time(page: str) -> int:
    soup = BeautifulSoup(page, "html.parser")
    row = soup.find("table").find_all("tr")[1]
    time = row.find_all("td")[8].string.strip()
    return int(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp())


def get_page_count(page: str) -> int:
    soup = BeautifulSoup(page, "html.parser")
    pagination_div = soup.find("div", class_="custom-links-pagination")

    if pagination_div is None:
        return 1

    pages_count = len(pagination_div.find_all("nobr"))
    return pages_count


def parse_standings(page: str) -> list[Standing]:
    """
    Parses the contest standings page and returns the contest standings.
    """
    print("Parsing standings page")
    soup = BeautifulSoup(page, "html.parser")
    standings_table = soup.find("table", class_="standings")

    if standings_table is None:
        raise RuntimeError("Can't find standings table")

    # four extra columns: rank, handle, solved, penalty
    problems_count = len(standings_table.find("tr", recursive=True).find_all("th")) - 4
    result: list[Standing] = []

    for row in standings_table.find_all("tr", {"participantid": True}):
        # column order: rank, handle, solved, penalty, problem1, problem2, ...
        cells = row.find_all("td", recursive=False)

        rank = cells[0].string.strip()
        handle = cells[1].find("a")["href"].split("/")[-1].strip().lower()
        solved = cells[2].string.strip()
        solved = int(solved) if solved else 0
        penalty = cells[3].string.strip()
        penalty = int(penalty) if len(penalty) > 0 else 0

        # Virtual participation has a superscript tag in handle
        is_virtual_participation = cells[1].find("sup") is not None
        # In contest participation has a rank entry
        is_in_contest_submission = len(rank) > 0 and not is_virtual_participation

        if is_virtual_participation:
            participation_type = ParticipationType.VIRTUAL
            rank = int(rank)
        elif is_in_contest_submission:
            participation_type = ParticipationType.IN_CONTEST
            rank = int(rank)
        else:
            participation_type = ParticipationType.AFTER_CONTEST
            rank = None

        result.append(
            Standing(
                solved=solved,
                rank=rank,
                handle=handle,
                penalty=penalty,
                problem_results=parse_problem_cells(cells[4:], problems_count),
                participation_type=participation_type,
            )
        )

    print("Parsing standings page complete")
    return result


def parse_problem_cells(problem_cells, problems_count) -> list[ProblemResult]:
    """
    Parses the entries and stores the results in the "results" dictionary.
    It also stores the rank, number of solved problems and problem stats.
    """
    return [parse_problem_cell(problem_cells[i], i) for i in range(problems_count)]


def parse_problem_cell(problem_cell, i) -> ProblemResult:
    """
    Parses the problem cell and returns the problem stat.
    """
    is_accepted = (
        problem_cell.find("span", attrs={"class": "cell-accepted"}) is not None
    )
    submission_id: int | None = None
    submission_contest_time: int | None = None

    if is_accepted:
        ac_cell = problem_cell.find("span", attrs={"class": "cell-accepted"})
        time_cell = problem_cell.find("span", attrs={"class": "cell-time"})

        submission_id = int(problem_cell.attrs.get("acceptedsubmissionid"))
        time = time_cell.string.strip() if time_cell is not None else "00:00"

        hours, minutes = map(int, time.split(":"))
        submission_contest_time = hours * 60 + minutes

        tries = ac_cell.string.strip()[1:]
        # if the problem is accepted, the tries is the number of wrong submissions or
        # empty string if the problem is solved in the first try. So, we add 1 to the tries.
        tries = int(tries) + 1 if len(tries) > 0 else 1
    else:
        reject_cell = problem_cell.find("span", attrs={"class": "cell-rejected"})
        tries = reject_cell.string.strip()[1:]
        tries = int(tries) if len(tries) > 0 else 0

    return ProblemResult(
        tries=tries,
        submission_id=submission_id,
        submission_contest_minutes=submission_contest_time,
        is_accepted=is_accepted,
        index=chr(ord("A") + i),
    )
