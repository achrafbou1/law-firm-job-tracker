from apify_client import ApifyClientAsync

from src.settings import settings


class ApifyClientProvider:
    _client: ApifyClientAsync | None = None

    @classmethod
    def get_client(cls) -> ApifyClientAsync:
        if cls._client is None:
            cls._client = ApifyClientAsync(settings.apify_api_key)
        return cls._client
