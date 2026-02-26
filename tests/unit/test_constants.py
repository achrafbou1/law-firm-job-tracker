"""Unit tests for the constants module."""

from zoneinfo import ZoneInfo

import pycountry

from src.constants import TARGET_COUNTRY, TIMEZONE


class TestConstants:
    def test_timezone_is_new_york(self):
        """Test that TIMEZONE is set to America/New_York."""
        assert TIMEZONE == ZoneInfo('America/New_York')

    def test_target_country_is_usa(self):
        """Test that TARGET_COUNTRY matches pycountry US official name (lowercase)."""
        us = pycountry.countries.get(alpha_2='US')
        assert TARGET_COUNTRY == us.official_name.lower()
        assert TARGET_COUNTRY == 'united states of america'
