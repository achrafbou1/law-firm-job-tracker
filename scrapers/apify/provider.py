from apify_client import ApifyClientAsync

from settings import settings


class ApifyClientProvider:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = ApifyClientAsync(settings.APIFY_API_KEY)
        return cls._client
