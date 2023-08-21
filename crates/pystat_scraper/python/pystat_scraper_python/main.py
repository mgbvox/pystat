"""The main module for the pystat_scraper_python package."""
import asyncio
import re
from pathlib import Path
from urllib import parse

import numpy.typing as npt
import pandas as pd
import requests
from github import Github

JSON = dict["JSONKey", "JSONVal"]
JSONKey = bool | str | float | int
JSONVal = JSONKey | list["JSONVal"] | JSON | None
"""A type alias for a json object."""

url_pat = re.compile(
    r"^https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)",
)


def match_github(data: str | None = "") -> str | None:
    return data if (re.search(url_pat, data) and "github" in data) else None


def extract_github_data(data: JSONVal) -> list[str]:
    """
    Extract GitHub urls from our data.

    Args:
        data: a json object.

    Returns:
        A list of GitHub urls found in the data.
    """
    found = []

    match data:
        case str():
            data: str
            if result := match_github(data):
                found = [result]

        case list():
            data: list
            for item in data:
                found.extend(extract_github_data(item))
        case dict():
            data: dict
            for value in data.values():
                found.extend(extract_github_data(value))
        case _:
            pass

    return found


def find_github_url(data: JSON) -> str:
    """
    Get the github url from our data, if it exists.

    Args:
        data: a json object.

    Returns:
        The GitHub url found in the data.
    """
    common_keys = ["Source Code", "Source", "Code", "Homepage", "Repository"]
    urls = data.get("info", {}).get("project_urls")
    candidate: JSONVal = None
    if urls and isinstance(urls, dict):
        for key in common_keys:
            if candidate := urls.get(key):
                break
            if candidate := urls.get(key.lower()):
                break
            if candidate := urls.get(key.upper()):
                break

    match candidate:
        case str():
            candidate: str
            if found := match_github(candidate):
                return found
        case _:
            pass

    # failing the above, brute force search for github url:

    found = list(set(extract_github_data(data)))

    match len(found):
        case 0:
            msg = "No GitHub url found!"
            raise ValueError(msg)
        case 1:
            return found[0]
        case _:
            msg = f"Too many GitHub urls found!: {found}"
            raise ValueError(msg)


def get_clone_url(source_url: str, hub: Github) -> str:
    path = parse.urlparse(source_url).path
    if path[0] == "/":
        path = path[1:]
    if path[-1] == "/":
        path = path[:-1]

    while path:
        try:
            np = hub.get_repo(path)
            clone_url = np.clone_url
            assert clone_url
            return clone_url
        except:
            path = "/".join(Path(path).parts[:-1])
    raise ValueError(f"Unable to find github clone url for {source_url=}")


async def get_data(pkg: str) -> dict[str, str]:
    pypi_url = f"https://pypi.org/pypi/{pkg}/json"
    pypi_response = requests.get(pypi_url)
    return pypi_response.json()


def get_top_pkgs() -> npt.NDArray[str]:
    data = requests.get("https://pypistats.org/top").text
    dfs = pd.read_html(data)
    data = dfs[-1]
    data.columns = ["rank", "pkg", "dls"]
    return data.pkg.values


def scrape() -> None:
    """Scrape the data for a GitHub url."""
    get_top_pkgs()
    asyncio.get_event_loop()


def main() -> None:
    """Enter our code - main entry point."""
    try:
        print(find_github_url(data))
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
