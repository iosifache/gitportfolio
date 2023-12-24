import importlib
import re
import sys
import typing
from datetime import datetime, timezone

from gitportfolio.exceptions import GitPortfolioError
from gitportfolio.facade import OrganisationFacade, RepositoryFacade
from gitportfolio.filters import RepositoryFacadePrivateFilter, filter_repos
from gitportfolio.formatter import to_list, to_repo_table
from gitportfolio.github import get_orgs, get_repos
from gitportfolio.logger import get_logger


def get_data_from_source(
    data_source_name: str,
) -> list[OrganisationFacade | RepositoryFacade | datetime]:
    get_logger().info(f'The data source "{data_source_name}" will be queried.')

    orgs = list(get_orgs())

    data: typing.Any = None
    if data_source_name == "now":
        data = datetime.now(tz=timezone.utc)
    elif data_source_name == "get_orgs":
        data = orgs
    elif data_source_name == "get_repos":
        data = get_repos(orgs)
    elif data_source_name == "get_public_repos":
        repos = list(get_repos(orgs))
        data = filter_repos(
            repos,
            RepositoryFacadePrivateFilter(is_private=False),
        )
    elif data_source_name == "get_private_repos":
        repos = list(get_repos(orgs))
        data = filter_repos(
            repos,
            RepositoryFacadePrivateFilter(is_private=True),
        )
    else:
        try:
            module = importlib.import_module(data_source_name)

            repos = list(get_repos(orgs))
            data = getattr(module, data_source_name)(orgs, repos)
        except (ImportError, AttributeError) as e:
            raise CustomFunctionNotImplementedError from e

    return data


def apply_operation(
    data: list[OrganisationFacade | RepositoryFacade | datetime],
    operation: str,
) -> str:
    get_logger().info(f'The operation "{operation}" will be applied.')

    if operation == "to_utc_string":
        if type(data) is not datetime:
            raise IncompatibleFormatterError

        return data.strftime("%Y-%m-%d %H:%M") + " UTC"  # type: ignore[attr-defined]

    if operation == "count":
        if not type(data[0] in [OrganisationFacade, RepositoryFacade]):
            raise IncompatibleFormatterError

        return str(len(data))  # type: ignore[arg-type]

    if operation == "to_list":
        if not type(data[0] in [OrganisationFacade, RepositoryFacade]):
            raise IncompatibleFormatterError

        return to_list(data)  # type: ignore[arg-type]

    if operation == "to_repo_table":
        if type(data[0]) is not RepositoryFacade:
            raise IncompatibleFormatterError

        return to_repo_table(data)  # type: ignore[arg-type]

    raise UnknownOperationError


def parse_single_query(
    query: str,
) -> str:
    if query.count("|") != 1:
        raise DSLSyntaxError

    data_source, operation = query.split("|")

    get_logger().info(f'The query "{query}" will be evaluated.')

    data = get_data_from_source(data_source)

    return apply_operation(data, operation)


def parse(custom_datasources_folder: str, text: str) -> str:
    get_logger().info("A parametrised text will be parsed.")

    sys.path.append(custom_datasources_folder)

    def replace_by_parsing(match: re.Match) -> str:
        query = match.group(1)

        return parse_single_query(query)

    return re.sub(
        r"<!-- gitportfolio: ([a-zA-Z_|]+) -->",
        replace_by_parsing,
        text,
    )


class DSLSyntaxError(GitPortfolioError):
    """The syntax (<datasource>|<processing_op>) is not respected."""


class CustomFunctionNotImplementedError(GitPortfolioError):
    """The called custom function is not implemented."""


class IncompatibleFormatterError(GitPortfolioError):
    """A data source was used with an incompatible formatter."""


class UnknownOperationError(GitPortfolioError):
    """The used operation is unknown."""
