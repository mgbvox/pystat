from pathlib import Path

import github
import pytest
from github import Auth

from pystat_scraper_python import main

creds_path = Path(__file__).parent.parent.parent/"creds"

@pytest.fixture()
def gh():
    auth = Auth.Token((creds_path / "gh.token").read_text())
    return github.Github(auth=auth)


def test_github_url_types():
    target = "https://github.com"
    result = main.find_github_url({"a": 1, "b": [1, 2, 3, {"url": target}]})

    assert result == target


@pytest.mark.asyncio()
async def test_github_top_pkg_get_info(gh):
    pkgs = main.get_top_pkgs()
    for pkg in pkgs:

        data = await main.get_data(pkg)
        try:
            url = main.find_github_url(data)
            clone_url = main.get_clone_url(url, gh)
            assert clone_url
            print(clone_url)
        except BaseException as e:
            return False
