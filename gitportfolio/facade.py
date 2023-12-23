from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class RepositoryFacade:
    name: str
    description: str
    owner: str
    creation_date: datetime
    last_push: datetime
    languages: list[str]
    tags: list[str]
    stars_count: int
    is_private: bool
    is_fork: bool
    is_archived: bool
    is_shown: bool

    @property
    def link(self) -> str:
        return f"https://github.com/{self.owner}/{self.name}"

    def as_array(self) -> list:
        return list(asdict(self).values())

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class OrganisationFacade:
    name: str
    login: str
    excluded: bool = False

    @property
    def link(self) -> str:
        return f"https://github.com/{self.login}"
