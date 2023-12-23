import importlib
import re
import typing

from gitportfolio.exceptions import GitPortfolioError
from gitportfolio.facade import OrganisationFacade, RepositoryFacade
from gitportfolio.filters import RepositoryFacadePrivateFilter, filter_repos
from gitportfolio.formatter import to_list, to_repo_table
from gitportfolio.github import get_orgs, get_repos


def get_data_from_source(
    config: dict,
    custom_datasources_folder: str,
    data_source_name: str,
) -> list[OrganisationFacade | RepositoryFacade]:
    orgs = list(get_orgs(config))

    data: typing.Any = None
    if data_source_name == "get_orgs":
        data = orgs
    elif data_source_name == "get_repos":
        data = get_repos(config, orgs)
    elif data_source_name == "get_public_repos":
        repos = list(get_repos(config, orgs))
        data = filter_repos(
            repos,
            RepositoryFacadePrivateFilter(is_private=False),
        )
    elif data_source_name == "get_private_repos":
        repos = list(get_repos(config, orgs))
        data = filter_repos(
            repos,
            RepositoryFacadePrivateFilter(is_private=True),
        )
    else:
        try:
            module = importlib.import_module(
                "." + data_source_name,
                package=custom_datasources_folder,
            )

            data = getattr(module, data_source_name)()
        except (ImportError, AttributeError) as e:
            raise CustomFunctionNotImplementedError from e

    return data


def apply_operation(
    data: list[OrganisationFacade | RepositoryFacade],
    operation: str,
) -> str:
    if operation == "count":
        return str(len(data))

    if operation == "to_list":
        return to_list(data, is_phrased=True)

    if operation == "to_repo_table":
        if not type(data[0] in [OrganisationFacade, RepositoryFacade]):
            raise ToRepoListOverOrgsError

        return to_repo_table(data)  # type: ignore # noqa: arg-type

    raise UnknownOperationError


def parse_single_query(
    config: dict,
    custom_datasources_folder: str,
    query: str,
) -> str:
    if query.count("|") != 1:
        raise DSLSyntaxError

    data_source, operation = query.split("|")

    data = get_data_from_source(config, custom_datasources_folder, data_source)

    return apply_operation(data, operation)


def parse(config: dict, custom_datasources_folder: str, text: str) -> str:
    def replace_by_parsing(match: re.Match) -> str:
        query = match.group(1)

        return parse_single_query(config, custom_datasources_folder, query)

    return re.sub(
        r"<!-- gitportfolio: ([a-zA-Z_|]+) -->",
        replace_by_parsing,
        text,
    )


class DSLSyntaxError(GitPortfolioError):
    """The syntax (<datasource>|<processing_op>) is not respected."""


class CustomFunctionNotImplementedError(GitPortfolioError):
    """The called custom function is not implemented."""


class ToRepoListOverOrgsError(GitPortfolioError):
    """The to_repo_table cannot be applied over a list of organisations."""


class UnknownOperationError(GitPortfolioError):
    """The used operation is unknown."""
