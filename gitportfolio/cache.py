from __future__ import annotations

import pickle
import typing
from pathlib import Path

from gitportfolio.logger import get_logger

REPOS_BACKUP = "repos.pickle"

if typing.TYPE_CHECKING:
    from gitportfolio.facade import RepositoryFacade


def dump_repos_to_file(
    cache_folder: str,
    repos: list[RepositoryFacade],
) -> None:
    with Path(cache_folder).joinpath(REPOS_BACKUP).open(mode="wb") as file:
        file.write(pickle.dumps(repos))

        get_logger().info("The repos were dumped into the cache file.")


def get_cached_repos(cache_folder: str) -> list[RepositoryFacade]:
    with Path(cache_folder).joinpath(REPOS_BACKUP).open(mode="rb") as file:
        content = pickle.loads(file.read())

        get_logger().info("The repos were read from the cache.")

        return content
