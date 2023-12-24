from __future__ import annotations

import typing

from github import Auth, Github
from github.Repository import Repository

from gitportfolio.cache import Cache
from gitportfolio.config import Configuration
from gitportfolio.facade import OrganisationFacade, RepositoryFacade
from gitportfolio.logger import get_logger

REPOS_CACHE_KEY = "repos"
ORGS_CACHE_KEY = "orgs"

orgs: list[OrganisationFacade] = []
repos: list[RepositoryFacade] = []


def get_orgs() -> typing.Generator[OrganisationFacade, None, None]:
    config = Configuration().get_config()
    pat = Configuration().get_github_pat()

    auth = Auth.Token(
        pat,
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


def create_repo_facade(repo: Repository) -> RepositoryFacade:
    config = Configuration().get_config()
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
    repo: Repository | RepositoryFacade,
) -> bool:
    config = Configuration().get_config()

    owner = repo.owner.login if type(repo) == Repository else repo.owner
    get_logger().info(
        f'Checking if the repository "{owner}/{repo.name}" should be skipped.',
    )

    repo_config = config["repos"].get(repo.name, {}).get("shown", True)
    if not repo_config:
        return True

    return any(org.login == owner and org.excluded for org in orgs)


def update_meta_from_config(
    repo: RepositoryFacade,
) -> RepositoryFacade:
    config = Configuration().get_config()
    repo_config = config["repos"].get(repo.name, {})

    repo.is_shown = repo_config.get("shown", True)
    repo.tags = repo_config.get("tags", [])

    return repo


def get_repos(
    orgs: list[OrganisationFacade],
) -> typing.Generator[RepositoryFacade, None, None]:
    Configuration().get_config()
    pat = Configuration().get_github_pat()

    auth = Auth.Token(
        pat,
    )
    github_client = Github(auth=auth)

    repos = Cache().get_cached_object(REPOS_CACHE_KEY)
    if repos:
        for repo in repos:
            repo = update_meta_from_config(repo)

            if is_repo_skipped(orgs, repo):
                get_logger().info(
                    f'The repository "{repo.name}" was skipped.',
                )

                continue

            yield repo

    else:
        repos = []
        for repo in github_client.get_user().get_repos():
            if is_repo_skipped(orgs, repo):
                get_logger().info(
                    f'The repository "{repo.name}" was skipped.',
                )

                continue

            repo_facade = create_repo_facade(repo)
            repo_facade = update_meta_from_config(repo_facade)

            get_logger().info(
                f'The repository "{repo_facade.name}" was fetched from'
                " GitHub.",
            )

            if repo_facade.is_shown:
                repos.append(repo_facade)
                yield repo_facade

        Cache().cache_object(REPOS_CACHE_KEY, repos)

    github_client.close()
