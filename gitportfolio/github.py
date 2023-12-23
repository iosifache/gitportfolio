from __future__ import annotations

import typing

from github import Auth, Github
from gitportfolio.config import get_github_pat
from gitportfolio.facade import OrganisationFacade, RepositoryFacade

if typing.TYPE_CHECKING:
    from github.Repository import Repository

orgs: list[OrganisationFacade] = []
repos: list[RepositoryFacade] = []


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
    owner = repo.owner

    return any(org.name == owner and org.excluded for org in orgs)


def get_repos(
    config: dict,
    orgs: list[OrganisationFacade],
) -> typing.Generator[RepositoryFacade, None, None]:
    global repos

    auth = Auth.Token(
        get_github_pat(),
    )
    github_client = Github(auth=auth)

    if repos:
        yield from repos

        return

    for repo in github_client.get_user().get_repos():
        if is_repo_skipped(orgs, repo):
            continue

        repo_facade = create_repo_facade(repo, config)

        repo_config = config["repos"].get(repo_facade.name, {})
        repo_facade.is_shown = repo_config.get("shown", True)
        repo_facade.tags = repo_config.get("tags", [])

        repos.append(repo_facade)

        yield repo_facade

    github_client.close()


def get_orgs(config: dict) -> typing.Generator[OrganisationFacade, None, None]:
    global orgs

    auth = Auth.Token(
        get_github_pat(),
    )
    github_client = Github(auth=auth)

    if orgs:
        yield from orgs

        return

    username = github_client.get_user().login
    for org in github_client.get_user(username).get_orgs():
        org_facade = OrganisationFacade(org.name or "", org.login)

        org_config = config["orgs"].get(org_facade.name, {})
        org_facade.excluded = org_config.get("excluded", False)

        orgs.append(org_facade)

        yield org_facade

    github_client.close()
