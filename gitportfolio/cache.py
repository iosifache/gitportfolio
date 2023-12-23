from __future__ import annotations

import pickle
import typing
from pathlib import Path

REPOS_BACKUP = "repos.pickle"

if typing.TYPE_CHECKING:
    from gitportfolio.facade import RepositoryFacade


def dump_repos_to_file(
    cache_folder: str,
    repos: list[RepositoryFacade],
) -> None:
    with Path(cache_folder).joinpath(REPOS_BACKUP).open(mode="wb") as file:
        file.write(pickle.dumps(repos))


def get_cached_repos(cache_folder: str) -> list[RepositoryFacade]:
    with Path(cache_folder).joinpath(REPOS_BACKUP).open(mode="rb") as file:
        content = file.read()

        return pickle.loads(content)
