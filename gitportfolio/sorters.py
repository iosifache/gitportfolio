from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from facade import RepositoryFacade


def sort_repos_by_member(
    repos: list[RepositoryFacade],
    member_name: str,
    *,
    reverse: bool = False,
) -> list[RepositoryFacade]:
    repos.sort(key=lambda x: x.as_dict().get(member_name, 0), reverse=reverse)

    return repos
