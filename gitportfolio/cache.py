from __future__ import annotations

import pickle
import typing
from pathlib import Path

from gitportfolio.exceptions import GitPortfolioError
from gitportfolio.helpers import Singleton
from gitportfolio.logger import get_logger

BACKUP_EXTENSION = ".pickle"


class Cache(metaclass=Singleton):
    disabled: bool
    cache_folder: str
    cache: dict[str, object] = {}

    def __init__(
        self,
        cache_folder: str = "",
        *,
        disabled: bool = False,
    ) -> None:
        self.disabled = disabled

        if not disabled and cache_folder == "":
            raise UnspecifiedCacheFolderError

        if disabled:
            get_logger().info(
                "The cache is disabled.",
            )
        else:
            get_logger().info(
                f'The cache was initialised with the folder "{cache_folder}".',
            )

        self.cache_folder = cache_folder

    def cache_object(
        self,
        identifier: str,
        obj: typing.Any,
    ) -> None:
        # In-memory caching
        self.cache[identifier] = obj

        if self.disabled:
            return

        # File-based caching
        with Path(self.cache_folder).joinpath(
            identifier + BACKUP_EXTENSION,
        ).open(
            mode="wb",
        ) as file:
            file.write(pickle.dumps(obj))

            get_logger().info(
                f'The object "{identifier}" were dumped into the cache file.',
            )

    def get_cached_object(self, identifier: str) -> typing.Any:
        # Get from in-memory cache
        obj = self.cache.get(identifier, None)
        if obj is not None:
            return obj

        if self.disabled:
            return None

        # Get from the file-based cache
        path = Path(self.cache_folder).joinpath(
            identifier + BACKUP_EXTENSION,
        )

        if not path.exists():
            return None

        with path.open(
            mode="rb",
        ) as file:
            obj = pickle.loads(file.read())

            self.cache[identifier] = obj

            get_logger().info(
                f'The object "{identifier}" was read from the cache.',
            )

            return obj


class UnspecifiedCacheFolderError(GitPortfolioError):
    """The cache folder was not specified."""
