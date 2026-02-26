"""Centralized constants for the job scraper application."""

from zoneinfo import ZoneInfo

import pycountry

TIMEZONE = ZoneInfo('America/New_York')
_US = pycountry.countries.get(alpha_2='US')
TARGET_COUNTRY = _US.official_name.lower()
