import abc
from abc import ABC
from dataclasses import dataclass, field
from urllib.parse import urlparse

from src.services.airtable.models.job_listing import JobListing


@dataclass
class BaseScraper(ABC):
    urls: list[str]
    new_jobs: list[JobListing] = field(default_factory=list)
    previous_jobs: list[JobListing] = field(default_factory=list)

    @abc.abstractmethod
    def get_previous_jobs(self) -> None:
        ...

    @abc.abstractmethod
    async def get_new_jobs(self) -> None:
        ...

    async def run(self) -> list[JobListing]:
        """Scrape, diff, and return the merged job list."""
        self.get_previous_jobs()
        await self.get_new_jobs()
        return self.diff_check()

    @abc.abstractmethod
    def diff_check(self) -> list[JobListing]:
        ...

    def __post_init__(self):
        for url in self.urls:
            parsed = urlparse(url)
            if not (parsed.scheme and parsed.netloc):
                raise ValueError(f"Invalid URL: {url}")
