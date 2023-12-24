from __future__ import annotations

from typing import TYPE_CHECKING

from gitportfolio.filters import (
    RepositoryFacadeOwnerFilter,
    RepositoryFacadePrivateFilter,
    RepositoryFacadeTagsFilter,
    filter_repos,
)

if TYPE_CHECKING:
    from gitportfolio.facade import OrganisationFacade, RepositoryFacade


def get_education_repos(
    _: list[OrganisationFacade],
    repos: list[RepositoryFacade],
) -> list[RepositoryFacade]:
    repos = filter_repos(
        repos,
        RepositoryFacadePrivateFilter(is_private=False),
    )
    repos = filter_repos(repos, RepositoryFacadeOwnerFilter("iosifache"))
    repos = filter_repos(
        repos,
        RepositoryFacadeTagsFilter(["masters", "bachelors", "highschool"]),
    )

    return repos
