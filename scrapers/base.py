import abc
from abc import ABC
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class BaseScraper(ABC):
    url: str

    @abc.abstractmethod
    def run(self):
        pass

    def __post_init__(self):
        parsed = urlparse(self.url)
        if not (parsed.scheme and parsed.netloc):
            raise ValueError(f"Invalid URL: {self.url}")