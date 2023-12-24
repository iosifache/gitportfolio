<p align="center">
    <img src="others/banner.webp" height="256" alt="GitPortfolio logo"/>
</p>
<h2 align="center">GitPortfolio</h2>

## Description

**GitPortfolio** is **an opinionated template engine that replaces placeholders in files with data derived from an analysis of your GitHub profile and repositories**. When the tool is run repeatedly, it also uses a **cache** to reduce the amount of queries to the GitHub API.

## Data sources

A data source specifies where the data is retrieved from.

The following data sources are available:

| Data source ID      | Description                                                                             | Return type                                        |
| ------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `now`               | Returns the date on which the engine was run.                                           | `datetime`                                         |
| `get_orgs`          | Gets the organisations of the analysed user.                                            | List of  `OrganisationFacade`                      |
| `get_repos`         | Gets all repositories (both publich and private) of the analysed user.                  | List of  `RepositoryFacade`                        |
| `get_public_repos`  | Gets the public repositories of the analysed user.                                      | List of  `RepositoryFacade`                        |
| `get_private_repos` | Gets the private repositories of the analysed user.                                     | List of  `RepositoryFacade`                        |
| Custom IDs          | IDs correspondig to a custom data source (see [the next section](#custom-data-sources)) | List of `OrganisationFacade` or `RepositoryFacade` |

### Custom data sources

You can also write Python 3 code for custom data sources, which the engine will format and return.

1. Create a folder, `<folder_name>`, that will contain all implementations of the custom function.
2. Supposing that a function called `<function_name>` (which is also the ID of the function) should be defined, create a new Python source file in `<folder_name>/<function_name>.py`. The function names should be composed of alpha characters (`a` to `z` and `A` to `Z`) and `_`.
3. Place the following content in the file. Replace `<function_name>` with the name of your function.

    ```python
    from __future__ import annotations

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from gitportfolio.facade import OrganisationFacade, RepositoryFacade

    def <function_name>(
        orgs: list[OrganisationFacade],
        repos: list[RepositoryFacade],
    ) -> list[OrganisationFacade]|list[RepositoryFacade]:
        # Implementation returning a compatible list of objects
    ```

4. Leverages the available methods to ease the implementation of the function:
   - Filters for repositories, defined in `gitportfolio.filters`: All filters derives `RepositoryFacadeFilter` and can be applied with the `filter_repos` function defined in the same module.
   - The `sort_repos_by_member` function: It is defined in `gitportfolio.sorters`, and used to sort a list of repositories by a member.
5. Use `<function_name>` as a data source in your template files.
6. When running the `gitportfolio` command, add `--datasource <folder_name>`.

## Formatters

The formatters define how to format the data from the data source. The formatters should be consistent with the type of data given by the data source to which they are applied, as shown in the table below.

The following formatters are available:

| Formatter ID    | Description                                                    | Compatible types of returned data from data sources |
| --------------- | -------------------------------------------------------------- | --------------------------------------------------- |
| `count`         | Counts the entries in the data source.                         | List of `OrganisationFacade` or `RepositoryFacade`  |
| `to_repo_table` | Creates a table with repositories.                             | List of `RepositoryFacade`                          |
| `to_list`       | Outputs a list with repositories or organisations.             | List of `OrganisationFacade` or `RepositoryFacade`  |
| `to_utc_string` | Formats a date as `<year>-<month>-<day> <hour>:<minutes> UTC`. | `datetime`                                          |

## Placeholders

The placeholders are composed of four parts:

- Two identification parts that are similar to an HTML comment;
- A data source ID; and
- A formatter ID.

Therefore, a placeholder should respect the following format:

```text
<!-- gitportfolio: (?<datasource_id>[a-zA-Z_]+)|(?<formatter_id>[a-zA-Z_]+) -->
```

## Configuration

The configuration file is a YAML file with metadata used to enrich the data fetched from GitHub. It should respect the following format:

```yaml
orgs:                                   # Additional metadata for organisations

  canonical:                            # One entry per organisation

    excluded: true                      # Boolean indicating if the repositories
                                        # in this organisation should not be
                                        # included in the output

repos:                                  # Additional metadata for repositories

  "<owner>/<repo_name>":                # One entry per organisation

    shown: <true|false>                 # Boolean indicating if the repository
                                        # is included in the output

    tags:                               # List of tags attached to the
                                        # repository

      - <tag>                           # Tag

tags:                                   # Tags metadata (unused)

  <tag>:                                # One entry for each tag used for
                                        # repositories

    description: <description>      # Description
```

The file might be empty because all members are optional.

## Usage

1. GitPorfolio requires a GitHub personal access token (PAT) to authenticate the requests to the GitHub API. Follow [the official guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) to get a GitHub PAT. Its value will be referenced as `<github_pat>` in the next sections.
2. Set the GitHub PAT as an environment variable:

    ```bash
    export GITHUB_PAT="<github_pat>"
    ```

3. Create a configuration respecting [the format](#configuration).
4. Run the engine over a template.

    ```bash
    gitportfolio                            \
        --config config.yaml                \ # Path to the configuration
        --cache cache                       \ # Caching folder
        --datasources custom_datasources    \ # Folder with custom data sources
        --template TEMPLATE.md              \ # Template document
        --output PROFILE.md                 \ # Output file
        --verbose                           \ # Enables logging,
        --caching                           \ # Enables the cache.
        --update                            \ # Enables automatic update of the
                                              # configuration.
    ```

Most of the GitPortfolio arguments and flags used above are optional. Please check the manual (`gitportfolio --help`) to deduce what parameters fit your needs.

## Further improvements

A few aspects of GitPortfolio can be improved:

- Support for repositories with the same name under different organisations; and
- A YAML schema (based on the existing description from this document) for validating the configurations.

## Acknowledgements

This project's logo and banner were created with [Adobe Firefly](https://firefly.adobe.com).
