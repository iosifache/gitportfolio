from __future__ import annotations

import typing

from github import Auth, Github

from gitportfolio.cache import Cache
from gitportfolio.config import get_github_pat
from gitportfolio.facade import OrganisationFacade, RepositoryFacade
from gitportfolio.logger import get_logger

if typing.TYPE_CHECKING:
    from github.Repository import Repository

REPOS_CACHE_KEY = "repos"
ORGS_CACHE_KEY = "orgs"

orgs: list[OrganisationFacade] = []
repos: list[RepositoryFacade] = []


def get_orgs(config: dict) -> typing.Generator[OrganisationFacade, None, None]:
    auth = Auth.Token(
        get_github_pat(),
    )
    github_client = Github(auth=auth)

    orgs = Cache().get_cached_object(ORGS_CACHE_KEY)
    if orgs:
        yield from orgs
    else:
        username = github_client.get_user().login

        orgs = []
        for org in github_client.get_user(username).get_orgs():
            org_facade = OrganisationFacade(org.name or "", org.login)

            org_config = config["orgs"].get(org.login, {})
            org_facade.excluded = org_config.get("excluded", False)

            orgs.append(org_facade)

            get_logger().info(
                f"The organisation {org_facade.name} was fetched from GitHub.",
            )

            yield org_facade

        Cache().cache_object(ORGS_CACHE_KEY, orgs)

    github_client.close()


def create_repo_facade(repo: Repository, config: dict) -> RepositoryFacade:
    repo_config = config["repos"].get(repo.name, {})

    return RepositoryFacade(
        repo.name,
        repo.description,
        repo.owner.login,
        repo.created_at,
        repo.pushed_at,
        list(repo.get_languages().keys()),
        repo_config.get("tags", []),
        repo.stargazers_count,
        repo.private,
        repo.fork,
        repo.archived,
        repo_config.get("shown", True),
    )


def is_repo_skipped(
    orgs: list[OrganisationFacade],
    repo: Repository,
) -> bool:
    owner = repo.owner.login

    get_logger().info(
        f'Checking if the repository "{owner}/{repo.name}" should be skipped.',
    )

    return any(org.login == owner and org.excluded for org in orgs)


def get_repos(
    config: dict,
    orgs: list[OrganisationFacade],
) -> typing.Generator[RepositoryFacade, None, None]:
    auth = Auth.Token(
        get_github_pat(),
    )
    github_client = Github(auth=auth)

    repos = Cache().get_cached_object(REPOS_CACHE_KEY)
    if repos:
        yield from repos

    else:
        repos = []
        for repo in github_client.get_user().get_repos():
            if is_repo_skipped(orgs, repo):
                get_logger().info(
                    f'The repository "{repo.name}" was skipped.',
                )

                continue

            repo_facade = create_repo_facade(repo, config)

            repo_config = config["repos"].get(repo_facade.name, {})
            repo_facade.is_shown = repo_config.get("shown", True)
            repo_facade.tags = repo_config.get("tags", [])

            repos.append(repo_facade)

            get_logger().info(
                f'The repository "{repo_facade.name}" was fetched from'
                " GitHub.",
            )

            if repo_facade.is_shown:
                yield repo_facade

        Cache().cache_object(REPOS_CACHE_KEY, repos)

    github_client.close()
