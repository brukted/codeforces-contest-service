from math import inf
import asyncio
from typing import Iterable
from models.domain.problem import Problem
from models.domain.problem_result import ProblemResult
from models.domain.standing import ParticipationType, Standing
from models.domain.submission import Submission
from models.requests.contest_summary_request import ContestSummaryRequest
from models.responses.contest_summary import ContestSummary, SingleRow
from scraper.page_loader import PageLoader
from scraper.problems_page_parser import parse_problems
from scraper.standing_page_parser import get_page_count, parse_standings
from scraper.status_page_parser import get_status_page_count, parse_status_page


class CodeForcesService:
    def __init__(self, page_loader: PageLoader):
        self.page_loader: PageLoader = page_loader

    async def get_contest_problems(self, gym_id: int) -> list[Problem]:
        print(f"Retrieving contest problems page")
        page = await self.page_loader.get_gym_page(gym_id)
        return parse_problems(page)

    async def get_contest_standings(self, gym_id: int):
        page = await self.page_loader.get_standings_page(gym_id)
        pages_count = get_page_count(page)
        result: list[Standing] = []

        # Semaphore is used to limit the number of concurrent requests to the server
        sem = asyncio.Semaphore(6)

        async def get_page(page_index: int):
            async with sem:
                print(f"Retrieving standings page {page_index} / {pages_count}")
                page = await self.page_loader.get_standings_page(gym_id, page_index)
                return page

        async def get_standings(page_index: int):
            page = await get_page(page_index)
            return parse_standings(page)

        tasks = [get_standings(page_index) for page_index in range(1, pages_count + 1)]
        standings = await asyncio.gather(*tasks)

        for standing in standings:
            result.extend(standing)

        return result

    async def get_contest_submissions(self, gym_id: int):
        page = await self.page_loader.get_status_page(gym_id, 1)
        pages_count = get_status_page_count(page)
        result: list[Submission] = []

        for page_index in range(1, pages_count + 1):
            print(f"Retrieving submissions page {page_index} / {pages_count}")
            page = await self.page_loader.get_status_page(gym_id, page_index)
            result.extend(parse_status_page(page))

        return result

    def __correct_rank(self, standings: Iterable[Standing]) -> list[Standing]:
        result: list[Standing] = sorted(standings, key=lambda standing: standing.rank)
        for i, standing in enumerate(result):
            standing.rank = i + 1
        return result

    def __remove_dual_participation(self, standings: list[Standing]) -> list[Standing]:
        """
        Removes participants' virtual participation from the contest if they have already participated in the contest in
        person and corrects the ranks.
        """

        # Identify the participants who have participated in the contest in person and virtually
        in_contest_participants = set(
            map(
                lambda st: st.handle,
                filter(
                    lambda st: st.participation_type == ParticipationType.IN_CONTEST,
                    standings,
                ),
            )
        )
        virtual_participants = set(
            map(
                lambda st: st.handle,
                filter(
                    lambda st: st.participation_type == ParticipationType.VIRTUAL,
                    standings,
                ),
            )
        )
        dual_participants = in_contest_participants.intersection(virtual_participants)

        result: list[Standing] = []

        for standing in standings:
            if (
                standing.participation_type == ParticipationType.IN_CONTEST
                or standing.handle not in dual_participants
            ) and standing.participation_type != ParticipationType.AFTER_CONTEST:
                result.append(standing)

        return result

    async def get_contest_summary(
        self, request: ContestSummaryRequest
    ) -> ContestSummary:
        submissions = await self.get_contest_submissions(request.gym_id)
        standings = await self.get_contest_standings(request.gym_id)
        problems = await self.get_contest_problems(request.gym_id)

        request.handles = map(lambda handle: handle.lower(), request.handles)

        submissions_lookup: dict[int, Submission] = {sub.id: sub for sub in submissions}

        # remove non in contest participation if virtual disabled
        standings = list(
            filter(
                lambda standing: standing.participation_type
                == ParticipationType.IN_CONTEST
                or (
                    standing.participation_type == ParticipationType.VIRTUAL
                    and request.virtual_enabled
                ),
                standings,
            )
        )

        if request.virtual_enabled:
            standings = self.__remove_dual_participation(standings)

        standings = self.__correct_rank(standings)

        # Earliest standing for each handle is used, if multiple encountered
        earliest_standing: dict[str, tuple[int, Standing]] = {}

        def get_submission_time(prob_res: ProblemResult):
            if prob_res.is_accepted:
                return submissions_lookup[prob_res.submission_id].submission_time_utc
            else:
                return inf

        for standing in standings:
            current = (
                dict[standing.handle]
                if standing.handle in earliest_standing
                else (inf, standing)
            )
            earliest_submission_time = min(
                map(get_submission_time, standing.problem_results)
            )

            if (
                standing.participation_type == ParticipationType.VIRTUAL
                and earliest_submission_time > request.virtual_deadline_utc
            ):
                continue

            earliest_standing[standing.handle] = min(
                current, (earliest_submission_time, standing)
            )

        summary: ContestSummary = ContestSummary(total_problems=len(problems), rows={})

        for handle in request.handles:
            if handle not in earliest_standing:
                summary.rows[handle] = None
                continue
            _, standing = earliest_standing[handle]
            summary.rows[handle] = SingleRow(
                rank=standing.rank,
                ac_count=standing.solved,
                participation_type=standing.participation_type,
            )

        return summary
