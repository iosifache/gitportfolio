from __future__ import annotations

import os
import shutil
import typing
from pathlib import Path

import yaml

from gitportfolio.exceptions import GitPortfolioError
from gitportfolio.filters import RepositoryFacadePrivateFilter, filter_repos
from gitportfolio.helpers import Singleton
from gitportfolio.logger import get_logger

if typing.TYPE_CHECKING:
    from gitportfolio.facade import OrganisationFacade, RepositoryFacade


class Configuration(metaclass=Singleton):
    filename: str
    config: dict
    github_pat: str

    def __init__(self, filename: str = "") -> None:
        if getattr(self, "filename", None) is None and filename is None:
            raise ConfigurationPathNotSpecifiedError

        self.filename = filename
        self.config = self._read_config(filename)
        self.github_pat = self._get_github_pat()

    def _read_config(self, filename: str) -> dict:
        with Path(filename).open(mode="r", encoding="utf-8") as file:
            configuration = yaml.safe_load(file.read())

            get_logger().info("The configuration was read.")

            return configuration

    def _get_github_pat(self) -> str:
        pat = os.environ.get("GITHUB_PAT", None)

        if not pat:
            raise GitHubPatNotSetError

        get_logger().info(
            "The GitHub personal access token was found.",
        )

        return pat

    def get_config(self) -> dict:
        return self.config

    def get_github_pat(self) -> str:
        return self.github_pat

    def get_orgs_not_in_config(
        self,
        orgs: list[OrganisationFacade],
    ) -> typing.Generator[OrganisationFacade, None, None]:
        for org in orgs:
            if org.login not in self.config["orgs"]:
                get_logger().warn(
                    f'The organisation "{org.login}" is not configured.',
                )

                yield org

    def get_repos_not_in_config(
        self,
        repos: list[RepositoryFacade],
    ) -> typing.Generator[RepositoryFacade, None, None]:
        public_repos = filter_repos(
            repos,
            RepositoryFacadePrivateFilter(is_private=False),
        )

        for repo in public_repos:
            if repo.name not in self.config["repos"]:
                get_logger().warn(
                    f'The repository "{repo.name}" is not configured.',
                )

                yield repo

    def update_config(self, *, save: bool = False) -> None:
        # Bad pattern, but trying to avoid circular dependencies
        from gitportfolio.github import get_orgs, get_repos

        orgs = list(get_orgs())
        repos = list(get_repos(orgs))

        updates = 0

        for org in self.get_orgs_not_in_config(orgs):
            self.config["orgs"][org.login] = {
                "excluded": False,
            }

            updates += 1

        for repo in self.get_repos_not_in_config(repos):
            self.config["repos"][repo.name] = {
                "owner": repo.owner,
                "shown": True,
                "tags": [],
            }

            updates += 1

        if save and updates > 0:
            backup_filename = self.filename + ".bak"
            shutil.copyfile(self.filename, backup_filename)

            with Path(self.filename).open(mode="w") as config_file:
                config_file.write(yaml.dump(self.config))

                get_logger().info(
                    "The new configuration was saved. The previous one was"
                    f' backed up in "{backup_filename}".',
                )


class ConfigurationPathNotSpecifiedError(GitPortfolioError):
    """The configuration path should be specified."""


class GitHubPatNotSetError(GitPortfolioError):
    """The GITHUB_PAT environment variable is not set."""
