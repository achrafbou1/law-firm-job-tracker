from dataclasses import field, dataclass

from apify_client import ApifyClientAsync

from scrapers.apify.provider import ApifyClientProvider
from scrapers.base import BaseScraper


@dataclass
class ApifyScraper(BaseScraper):
    apify_client: ApifyClientAsync = field(default_factory=ApifyClientProvider.get_client)