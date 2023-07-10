import json
import os
from fastapi import FastAPI, HTTPException, Request
import httpcore
from models.domain.problem import Problem
from fastapi.responses import JSONResponse


from models.requests.contest_summary_request import ContestSummaryRequest
from models.responses.contest_summary import ContestSummary
from models.responses.jsend_response import JSendResponse
from scraper.page_loader import PageLoader

from dotenv import load_dotenv

from service.codefroces_service import CodeForcesService

load_dotenv()

configuration = {
    "handleOrEmail": os.getenv("CODEFORCES_HANDLE"),
    "password": os.getenv("CODEFORCES_PASSWORD"),
}

app = FastAPI()


@app.exception_handler(httpcore.ConnectTimeout)
async def unicorn_exception_handler(request: Request, exc: httpcore.ConnectTimeout):
    return JSONResponse(
        status_code=500,
        content=json.dumps(JSendResponse(message="Connect timeout.", data=None)),
    )


@app.get("/")
def health_check() -> JSendResponse[None]:
    return JSendResponse(message="OK", data=None)


@app.post("/contest/{gym_id}/summary")
async def get_contest_summary(gym_id: int, request: ContestSummaryRequest):
    request.gym_id = gym_id
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_summary(request)
    )


@app.get("/contest/{gym_id}")
async def get_contest(gym_id: int):
    raise HTTPException(
        status_code=400,
        detail="Not implemented",
    )


@app.get("/contest/{gym_id}/submissions")
async def get_contest_submissions(gym_id: int):
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
async def get_contest_standings(gym_id: int):
    page_loader = PageLoader(configuration)
    await page_loader.authenticate()
    codeforces_service = CodeForcesService(page_loader)
    return JSendResponse(
        message="OK", data=await codeforces_service.get_contest_standings(gym_id)
    )
