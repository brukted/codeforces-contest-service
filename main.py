import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from models.domain.problem import Problem
from models.domain.standing import Standing
from models.domain.submission import Submission
from models.requests.contest_summary_request import ContestSummaryRequest
from models.responses.contest_summary import ContestSummary
from models.responses.jsend_response import JSendResponse
from scraper.page_loader import PageLoader
from service.codeforces_service import CodeForcesService

load_dotenv()

description = """
The CodeForces Contest API is a service that provides 
access to various features and information related to CodeForces contests. 
It allows users to retrieve contest summaries, submissions, problems, and standings for a specific contest.
"""

app = FastAPI(title="CodeForces Contest API", version="0.1.0", description=description)

configuration = {
    "handleOrEmail": os.getenv("CODEFORCES_HANDLE"),
    "password": os.getenv("CODEFORCES_PASSWORD"),
}


@app.exception_handler(httpx.ReadTimeout)
async def unicorn_exception_handler(request: Request, exc: httpx.ReadTimeout):
    return JSONResponse(
        status_code=500,
        content=JSendResponse(message="Connect timeout.", data=None).model_dump_json(),
    )


@app.get("/health-check")
def health_check() -> JSendResponse[None]:
    """Performs a health check for the API. Returns a JSendResponse indicating the status of the API."""
    return JSendResponse(message="OK", data=None)


@app.post("/contest/{gym_id}/summary")
async def get_contest_summary(
    gym_id: int, request: ContestSummaryRequest
) -> JSendResponse[ContestSummary]:
    """Retrieves a summary of a CodeForces contest with the specified gym ID.

    Note: Some contestants may be discarded based on virtual participation and deadline.
    """
    request.gym_id = gym_id
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_summary(request)
    )


@app.get("/contest/{gym_id}/submissions")
async def get_contest_submissions(gym_id: int) -> JSendResponse[list[Submission]]:
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_submissions(gym_id)
    )


@app.get("/contest/{gym_id}/problems")
async def get_contest_problems(gym_id: int) -> JSendResponse[list[Problem]]:
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_problems(gym_id)
    )


@app.get("/contest/{gym_id}/standings")
async def get_contest_standings(gym_id: int) -> JSendResponse[list[Standing]]:
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_standings(gym_id)
    )
