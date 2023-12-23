from __future__ import annotations

from pathlib import Path

import click

from gitportfolio.cache import Cache
from gitportfolio.config import read_config
from gitportfolio.dsl import parse
from gitportfolio.logger import disable_logger


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
    default=False,
    help="Boolean indicating if caching is enabled",
)
@click.option(
    "--verbose/--silent",
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

    Cache(cache, disabled=(not caching))

    with Path(template).open(mode="r") as template_file:
        template = template_file.read()
        readme = parse(configuration, datasources, template)

    with Path(output).open(mode="w") as output_file:
        output_file.write(readme)


if __name__ == "__main__":
    main()
