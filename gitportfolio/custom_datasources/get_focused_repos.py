from __future__ import annotations

from typing import TYPE_CHECKING

from gitportfolio.filters import (
    RepositoryFacadeArchivedFilter,
    RepositoryFacadeOwnerFilter,
    RepositoryFacadePrivateFilter,
    filter_repos,
)

if TYPE_CHECKING:
    from gitportfolio.facade import OrganisationFacade, RepositoryFacade


def get_focused_repos(
    _: list[OrganisationFacade],
    repos: list[RepositoryFacade],
) -> list[RepositoryFacade]:
    repos = filter_repos(
        repos,
        RepositoryFacadePrivateFilter(is_private=False),
    )
    repos = filter_repos(repos, RepositoryFacadeOwnerFilter(owner="iosifache"))
    repos = filter_repos(
        repos,
        RepositoryFacadeArchivedFilter(is_archived=False),
    )

    return repos
