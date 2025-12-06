import abc
from abc import ABC
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class BaseScraper(ABC):
    urls: list[str]

    @abc.abstractmethod
    async def run(self):
        pass

    def __post_init__(self):
        for url in self.urls:
            parsed = urlparse(url)
            if not (parsed.scheme and parsed.netloc):
                raise ValueError(f"Invalid URL: {url}")