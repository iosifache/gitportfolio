from __future__ import annotations

from typing import TYPE_CHECKING

from gitportfolio.filters import (
    RepositoryFacadeForkFilter,
    RepositoryFacadeOwnerFilter,
    RepositoryFacadePrivateFilter,
    RepositoryFacadeTagsFilter,
    filter_repos,
)

if TYPE_CHECKING:
    from gitportfolio.facade import OrganisationFacade, RepositoryFacade


def get_contribution_repos(
    _: list[OrganisationFacade],
    repos: list[RepositoryFacade],
) -> list[RepositoryFacade]:
    forks = filter_repos(
        repos,
        RepositoryFacadePrivateFilter(is_private=False),
    )
    forks = filter_repos(repos, RepositoryFacadeForkFilter(is_fork=True))

    repos = filter_repos(
        repos,
        RepositoryFacadePrivateFilter(is_private=False),
    )
    repos = filter_repos(
        repos,
        RepositoryFacadeOwnerFilter(owner="iosifache", inverse=True),
    )
    repos = filter_repos(
        repos,
        RepositoryFacadeTagsFilter(
            tags=["masters", "bachelors", "highschool"],
            inverse=True,
        ),
    )
    repos.extend(forks)

    return repos
