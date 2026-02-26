"""Unit tests for the base scraper."""

import pytest

from src.services.scrapers.base import BaseScraper


class TestBaseScraper:
    def test_invalid_url_raises_value_error(self):
        """Test that invalid URLs raise ValueError on initialization."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        with pytest.raises(ValueError) as exc_info:
            ConcreteScraper(urls=['not-a-url'])
        assert 'Invalid URL' in str(exc_info.value)

    def test_valid_urls_accepted(self):
        """Test that valid URLs are accepted."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        scraper = ConcreteScraper(urls=[
            'https://example.com/jobs',
            'http://another.com/careers'
        ])
        assert len(scraper.urls) == 2

    def test_empty_urls_allowed(self):
        """Test that empty URL list is allowed."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        scraper = ConcreteScraper(urls=[])
        assert scraper.urls == []

    def test_new_jobs_initialized_empty(self):
        """Test that new_jobs and previous_jobs are initialized empty."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        scraper = ConcreteScraper(urls=[])
        assert scraper.new_jobs == []
        assert scraper.previous_jobs == []

    def test_url_without_scheme_invalid(self):
        """Test that URLs without scheme are invalid."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        with pytest.raises(ValueError):
            ConcreteScraper(urls=['example.com/jobs'])

    def test_url_without_netloc_invalid(self):
        """Test that URLs without netloc are invalid."""
        class ConcreteScraper(BaseScraper):
            def get_previous_jobs(self): pass
            async def get_new_jobs(self): pass
            def diff_check(self): return []

        with pytest.raises(ValueError):
            ConcreteScraper(urls=['https://'])
