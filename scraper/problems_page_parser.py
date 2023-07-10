from typing import Iterable
from bs4 import BeautifulSoup, Tag
from models.domain.problem import Problem


def parse_problems(page: str) -> list[Problem]:
    """
    Parses the contest problems page and returns the problems.
    """
    print("Parsing problems")
    soup = BeautifulSoup(page, "html.parser")
    problems_table = soup.find("table", class_="problems")

    if problems_table is None:
        raise RuntimeError("Can't find problems table")

    problems = []
    rows = problems_table.find_all("tr", recursive=True)

    for row in rows[1:-1]:
        # column order: index, name, submit, submission count, management
        cells: Iterable[Tag] = row.find_all("td", recursive=False)
        problem_index = cells[0].find("a").string.strip()
        problem_name = cells[1].find("a", recursive=True).contents[1].strip()
        original_problem_url = None

        if len(cells) == 5:
            problem_tags = cells[4].find_all("a")
            if len(problem_tags) == 3:
                original_problem_url = problem_tags[2]["href"]

        problems.append(
            Problem(
                index=problem_index,
                in_contest_name=problem_name,
                original_problem_url=original_problem_url,
            )
        )

    print("Parsing problems complete")
    return problems
