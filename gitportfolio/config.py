from __future__ import annotations

import os
import typing
from pathlib import Path

import yaml

from gitportfolio.exceptions import GitPortfolioError
from gitportfolio.filters import RepositoryFacadePrivateFilter, filter_repos

if typing.TYPE_CHECKING:
    from gitportfolio.facade import RepositoryFacade


def read_config(filename: str) -> dict:
    with Path(filename).open(mode="r", encoding="utf-8") as file:
        return yaml.safe_load(file.read())


def get_repos_not_in_config(
    config: dict,
    repos: list[RepositoryFacade],
) -> typing.Generator[RepositoryFacade, None, None]:
    public_repos = filter_repos(
        repos,
        RepositoryFacadePrivateFilter(is_private=False),
    )

    for repo in public_repos:
        if repo.name not in config["repos"]:
            yield repo


def get_github_pat() -> str:
    pat = os.environ.get("GITHUB_PAT", None)

    if not pat:
        raise GitHubPatNotSetError

    return pat


class GitHubPatNotSetError(GitPortfolioError):
    """The GITHUB_PAT environment variable is not set."""
