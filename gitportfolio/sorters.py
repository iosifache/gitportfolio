from __future__ import annotations

from typing import TYPE_CHECKING

from gitportfolio.logger import get_logger

if TYPE_CHECKING:
    from facade import RepositoryFacade


def sort_repos_by_member(
    repos: list[RepositoryFacade],
    member_name: str,
    *,
    reverse: bool = False,
) -> list[RepositoryFacade]:
    repos.sort(key=lambda x: x.as_dict().get(member_name, 0), reverse=reverse)

    get_logger().info("A list of repositories was filtered.")

    return repos
