from __future__ import annotations

import typing

from tabulate import tabulate

from gitportfolio.logger import get_logger

if typing.TYPE_CHECKING:
    from gitportfolio.facade import OrganisationFacade, RepositoryFacade


def trim_text(text: str, max_length: int) -> str:
    if not text:
        return text

    if len(text) > max_length:
        return text[: max_length - 3] + "..."

    return text


def tinify(text: str) -> str:
    if not text:
        return text

    return "<sup><sub>" + text + "</sub></sup>"


def to_repo_table(repos: list[RepositoryFacade]) -> str:
    get_logger().info("A list of repositories will be formatted as a table.")

    data = []
    for repo in repos:
        get_logger().info(
            f'Repository "{repo.name}" will be added to a table.',
        )

        identifier = (
            f"[`{repo.owner}/{repo.name}`]"
            f"(https://github.com/{repo.owner}/{repo.name}) "
        )
        if repo.is_fork:
            identifier += "🪞"
        if repo.is_archived:
            identifier += "📦"
        identifier = tinify(identifier)

        description = tinify(trim_text(repo.description, 50))
        creation_date = repo.creation_date.strftime("%b%%20%Y")
        last_push = repo.last_push.strftime("%b%%20%Y")

        tags = " ".join([f"`#{tag}`" for tag in repo.tags])
        tags = tinify(tags)

        entry = [
            identifier,
            description,
            tags,
            (
                f"<img height='12px' alt='Created on: {creation_date}'"
                " src='https://img.shields.io/badge/"
                f"Created%20on-{creation_date}-black'/> "
                f"<img height='12px' alt='Last push on: {last_push}'"
                " src='https://img.shields.io/badge/"
                f"Last%20push%20on-{last_push}-green'/> "
                f"<img height='12px' alt='Stars: {repo.stars_count}'"
                " src='https://img.shields.io/badge/"
                f"Stars-{repo.stars_count}-yellow'/> "
            ),
        ]
        data.append(entry)

    return tabulate(
        data,
        headers=["Identifier", "Description", "Tags", "Metadata"],
        tablefmt="github",
    )


def to_list(
    items: list[RepositoryFacade | OrganisationFacade],
    *,
    is_phrased: bool = False,
) -> str:
    get_logger().info("A list of objects will be formatted as a list.")

    count = len(items)

    return "\n".join(
        [
            f"- [{org.name}]({org.link})"
            + (
                ("." if is_phrased else "")
                if index == count - 1
                else (
                    ("; and" if is_phrased else "")
                    if index == count - 2
                    else (";" if is_phrased else "")
                )
            )
            for index, org in enumerate(items)
        ],
    )
