from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from gitportfolio.logger import get_logger

if TYPE_CHECKING:
    from gitportfolio.facade import RepositoryFacade


class RepositoryFacadeFilter:
    @abstractmethod
    def is_accepted(self, repo: RepositoryFacade) -> bool:
        raise NotImplementedError


class RepositoryFacadeOwnerFilter(RepositoryFacadeFilter):
    owner: str
    inverse: bool

    def __init__(self, owner: str, *, inverse: bool = False) -> None:
        self.owner = owner
        self.inverse = inverse

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        same = repo.owner == self.owner

        return same if not self.inverse else not same


class RepositoryFacadeArchivedFilter(RepositoryFacadeFilter):
    is_archived: bool

    def __init__(self, *, is_archived: bool) -> None:
        self.is_archived = is_archived

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        return repo.is_archived == self.is_archived


class RepositoryFacadePrivateFilter(RepositoryFacadeFilter):
    is_private: bool

    def __init__(self, *, is_private: bool) -> None:
        self.is_private = is_private

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        return repo.is_private == self.is_private


class RepositoryFacadeShownFilter(RepositoryFacadeFilter):
    is_shown: bool

    def __init__(self, *, is_shown: bool) -> None:
        self.is_shown = is_shown

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        return repo.is_shown == self.is_shown


class RepositoryFacadeForkFilter(RepositoryFacadeFilter):
    is_fork: bool

    def __init__(self, *, is_fork: bool) -> None:
        self.is_fork = is_fork

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        return repo.is_fork == self.is_fork


class RepositoryFacadeTagsFilter(RepositoryFacadeFilter):
    tags: list[str]
    inverse: bool

    def __init__(self, tags: list[str], *, inverse: bool = False) -> None:
        self.tags = tags
        self.inverse = inverse

    def is_accepted(self, repo: RepositoryFacade) -> bool:
        is_in = any([tag in repo.tags for tag in self.tags])

        return is_in if not self.inverse else not is_in


def filter_repos(
    repos: list[RepositoryFacade],
    custom_filter: RepositoryFacadeFilter,
) -> list[RepositoryFacade]:
    get_logger().info(
        "A list of repositories will be filtered with"
        f" {custom_filter.__class__.__name__}.",
    )

    return [repo for repo in repos if custom_filter.is_accepted(repo)]
