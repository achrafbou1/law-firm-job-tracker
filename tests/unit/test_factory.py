"""Unit tests for the factory module."""

import pytest

from src.exceptions import UnsupportedATSType
from src.factories import SCRAPER_REGISTRY, law_firm_factory
from src.services.airtable.models.law_firm import AtsType
from src.services.scrapers.ats.greenhouse import GreenhouseScraper
from src.services.scrapers.ats.workday import WorkdayScraper


class MockLawFirm:
    """Mock LawFirm for testing without Airtable connection."""
    def __init__(self, ats_type: str, name: str = 'Test Firm'):
        self.ats_type = ats_type
        self.name = name


class TestFactory:
    def test_workday_factory_returns_workday_scraper(self):
        """Test that Workday ATS type returns WorkdayScraper."""
        law_firm = MockLawFirm(ats_type=AtsType.WORKDAY)
        scraper_cls = law_firm_factory(law_firm)
        assert scraper_cls == WorkdayScraper

    def test_greenhouse_factory_returns_greenhouse_scraper(self):
        """Test that Greenhouse ATS type returns GreenhouseScraper."""
        law_firm = MockLawFirm(ats_type=AtsType.GREENHOUSE)
        scraper_cls = law_firm_factory(law_firm)
        assert scraper_cls == GreenhouseScraper

    def test_unsupported_ats_raises_exception(self):
        """Test that unsupported ATS type raises UnsupportedATSType."""
        law_firm = MockLawFirm(ats_type='UnsupportedATS', name='Bad Firm')
        with pytest.raises(UnsupportedATSType) as exc_info:
            law_firm_factory(law_firm)
        assert 'UnsupportedATS' in str(exc_info.value)
        assert 'Bad Firm' in str(exc_info.value)

    def test_registry_contains_workday(self):
        """Test that the scraper registry contains Workday."""
        assert AtsType.WORKDAY in SCRAPER_REGISTRY
        assert SCRAPER_REGISTRY[AtsType.WORKDAY] == WorkdayScraper

    def test_registry_contains_greenhouse(self):
        """Test that the scraper registry contains Greenhouse."""
        assert AtsType.GREENHOUSE in SCRAPER_REGISTRY
        assert SCRAPER_REGISTRY[AtsType.GREENHOUSE] == GreenhouseScraper

    def test_none_ats_type_raises_exception(self):
        """Test that None ATS type raises UnsupportedATSType."""
        law_firm = MockLawFirm(ats_type=None)
        with pytest.raises(UnsupportedATSType):
            law_firm_factory(law_firm)
