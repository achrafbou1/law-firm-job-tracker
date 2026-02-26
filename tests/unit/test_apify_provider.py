"""Unit tests for the Apify provider singleton."""

from unittest.mock import create_autospec, patch

from apify_client import ApifyClientAsync

from src.services.scrapers.ats.apify_provider import ApifyClientProvider


class TestApifyClientProvider:
    def setup_method(self):
        """Reset the singleton before each test."""
        ApifyClientProvider._client = None

    def teardown_method(self):
        """Reset the singleton after each test."""
        ApifyClientProvider._client = None

    @patch('src.services.scrapers.ats.apify_provider.ApifyClientAsync')
    def test_get_client_creates_client_once(self, mock_client_cls):
        """Test that get_client creates client only once (singleton)."""
        mock_instance = create_autospec(ApifyClientAsync, instance=True)
        mock_client_cls.return_value = mock_instance

        # First call creates the client
        client1 = ApifyClientProvider.get_client()
        # Second call returns the same instance
        client2 = ApifyClientProvider.get_client()

        assert client1 is client2
        assert mock_client_cls.call_count == 1

    @patch('src.services.scrapers.ats.apify_provider.ApifyClientAsync')
    def test_get_client_uses_api_key_from_settings(self, mock_client_cls):
        """Test that the client is created with the API key from settings."""
        from src.settings import settings

        ApifyClientProvider.get_client()

        mock_client_cls.assert_called_once_with(settings.apify_api_key)
