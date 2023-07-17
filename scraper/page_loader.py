import os
import string
from bs4 import BeautifulSoup
import pickle
import httpx


class PageLoader:
    """
    Page loader is a class we use to load web pages.
    """

    def __init__(self, configuration) -> None:
        self.async_session = httpx.AsyncClient(follow_redirects=True, timeout=10)
        self.async_session.cookies.update({"__hs_opt_out": "no"})

        self.handle_or_email = configuration["handleOrEmail"]
        self.password = configuration["password"]

    async def authenticate(self):
        login = await self.async_session.get("https://codeforces.com/enter")
        ss = BeautifulSoup(login.text, features="html.parser")

        csrf_token = ss.find("span", {"class": "csrf-token"})["data-csrf"]

        payload = {
            "handleOrEmail": self.handle_or_email,
            "action": "enter",
            "password": self.password,
            "csrf_token": csrf_token,
        }

        print("Authenticating")
        res = await self.async_session.post(
            "https://codeforces.com/enter", data=payload
        )
        res.raise_for_status()
        print("Authentication Complete")

    async def get_standings_page(
        self, gym_id, page: int = 1, show_unofficial: bool = True
    ):
        url = f"https://codeforces.com/gym/{gym_id}/standings/page/{page}"
        payload = {
            "newShowUnofficialValue": show_unofficial,
            "action": "toggleShowUnofficial",
        }

        await self.async_session.post(url, data=payload)
        data = await self.async_session.get(url)
        data.raise_for_status()
        return data.text

    async def get_gym_page(self, gym_id: int) -> string:
        url = f"https://codeforces.com/gym/{gym_id}"
        data = await self.async_session.get(url)
        data.raise_for_status()
        return data.text

    async def get_submission_page(self, gym_id, submission_id):
        url = f"https://codeforces.com/gym/{gym_id}/submission/{submission_id}"
        cache_path = f"cache/submission/{gym_id}_{submission_id}.html"

        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        data = await self.async_session.get(url)
        data.raise_for_status()

        with open(cache_path, "wb") as f:
            f.write(data.content)
        return data.text

    async def get_status_page(self, gym_id, page_index):
        url = f"https://codeforces.com/gym/{gym_id}/status?pageIndex={page_index}&order=BY_JUDGED_DESC"
        cache_path = f"cache/status/{gym_id}_{page_index}.html"

        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()
        data = await self.async_session.get(url)
        data.raise_for_status()
        with open(cache_path, "wb") as f:
            f.write(data.content)
        return data.text
