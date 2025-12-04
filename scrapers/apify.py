from dataclasses import dataclass, field

from apify_client import ApifyClientAsync

from apify_provider import ApifyClientProvider
from scrapers.base import BaseScraper

@dataclass
class ApifyScraper(BaseScraper):
    apify_client: ApifyClientAsync = field(default_factory=ApifyClientProvider.get_client)