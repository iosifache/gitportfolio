from __future__ import annotations

import typing
from pathlib import Path

import click

from gitportfolio.cache import dump_repos_to_file, get_cached_repos
from gitportfolio.config import read_config
from gitportfolio.dsl import parse
from gitportfolio.github import get_orgs, get_repos
from gitportfolio.logger import disable_logger
from gitportfolio.sorters import sort_repos_by_member

if typing.TYPE_CHECKING:
    from gitportfolio.facade import RepositoryFacade


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    help="YAML configuration file",
)
@click.option(
    "--cache",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True,
    help="Cache folder (only if caching is used)",
)
@click.option(
    "--datasources",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True,
    help="Folder with custom implementation of datasources",
)
@click.option(
    "--template",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    help="Template file",
)
@click.option(
    "--output",
    type=click.Path(exists=False),
    required=True,
    help="Output file",
)
@click.option(
    "--caching/--no-caching",
    default=True,
    help="Boolean indicating if caching is enabled",
)
@click.option(
    "--verbose",
    default=False,
    help="Boolean indicating if information will be logged",
)
def main(
    config: str,
    cache: str,
    datasources: str,
    template: str,
    output: str,
    *,
    caching: bool,
    verbose: bool,
) -> None:
    if not verbose:
        disable_logger()

    configuration = read_config(config)

    repos: list[RepositoryFacade] = []
    if caching:
        repos = get_cached_repos(cache)
    else:
        orgs = list(get_orgs(configuration))
        repos = list(get_repos(configuration, orgs))
        dump_repos_to_file(cache, repos)

    repos = sort_repos_by_member(
        repos,
        "creation_date",
        reverse=True,
    )

    with Path(template).open(mode="r") as template_file:
        template = template_file.read()
        readme = parse(configuration, datasources, template)

    with Path(output).open(mode="w") as output_file:
        output_file.write(readme)


if __name__ == "__main__":
    main()