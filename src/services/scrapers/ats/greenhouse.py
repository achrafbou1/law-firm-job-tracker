"""Greenhouse ATS scraper implementation."""

import re

import pycountry

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.base import ApifyScraper
from src.services.scrapers.schemas.greenhouse import GreenhouseInput, GreenhouseJob

# Pre-build sets for US detection
_US = pycountry.countries.get(alpha_2='US')
_US_COUNTRY_NAME = _US.official_name.lower()

_US_STATE_CODES = {
    s.code.split('-')[1].lower()
    for s in pycountry.subdivisions.get(country_code='US')
}

_US_STATE_NAMES = {
    s.name.lower()
    for s in pycountry.subdivisions.get(country_code='US')
}

# Common US city names that frequently appear in job listings without state codes
_US_CITY_NAMES = {
    'boston', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
    'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose',
    'austin', 'jacksonville', 'san francisco', 'seattle', 'denver',
    'nashville', 'washington', 'miami', 'atlanta', 'portland', 'minneapolis',
    'detroit', 'charlotte', 'pittsburgh', 'cleveland', 'st. louis',
    'tampa', 'orlando', 'cincinnati', 'palo alto', 'silicon valley',
}


def _is_us_location(text: str) -> bool:
    """Check if a single location string looks like a US location."""
    # Strip common suffixes
    cleaned = re.sub(r'\s*(office|hq|headquarters)\s*$', '', text, flags=re.IGNORECASE).strip()
    token = re.sub(r'\.', '', cleaned).strip().lower()

    if not token:
        return False

    # Check last comma-separated part for state abbreviation: "New York, NY"
    last_part = token.rsplit(',', 1)[-1].strip()
    if last_part in _US_STATE_CODES:
        return True

    # Check if the whole cleaned string is a US state name: "New York Office" → "new york"
    if token in _US_STATE_NAMES:
        return True

    # Check if it matches a well-known US city: "Boston Office" → "boston"
    if token in _US_CITY_NAMES:
        return True

    return False


def resolve_country(location: str) -> str:
    """Determine country from a Greenhouse location string.

    Greenhouse locations come as:
    - "NY"
    - "New York, NY"
    - "Miami, FL"
    - "Washington, D.C."
    - "London, United Kingdom"
    - "Boston Office; New York Office; Washington DC Office"

    Returns a lowercased country name, or '' if nothing could be resolved.
    """
    if not location:
        return ''

    # Handle semicolon-separated multi-location strings
    parts = [p.strip() for p in re.split(r'[;]', location) if p.strip()]

    # Check if any part is a US location
    if any(_is_us_location(p) for p in parts):
        return _US_COUNTRY_NAME

    # For single locations, try the last comma-separated token against pycountry
    last_part = location.rsplit(',', 1)[-1].strip()
    token = re.sub(r'\.', '', last_part).strip().lower()

    if not token:
        return ''

    # US state abbreviation (handles "New York, NY")
    if token in _US_STATE_CODES:
        return _US_COUNTRY_NAME

    # Exact pycountry lookup (full names, alpha-2, alpha-3)
    try:
        country = pycountry.countries.lookup(last_part)
        return getattr(country, 'official_name', country.name).lower()
    except LookupError:
        pass

    # Fuzzy search as last resort ("USA", "UK", etc.)
    try:
        country = pycountry.countries.search_fuzzy(last_part)[0]
        return getattr(country, 'official_name', country.name).lower()
    except LookupError:
        pass

    return ''


class GreenhouseScraper(ApifyScraper):
    """Scraper for Greenhouse ATS job boards."""

    ACTOR_ID = 'jupri/greenhouse'

    async def get_new_jobs(self) -> None:
        """Fetch new jobs from Greenhouse using Apify actor."""
        run_input = GreenhouseInput.from_urls(self.urls)
        run = await self.apify_client.actor(self.ACTOR_ID).call(
            run_input=run_input.model_dump()
        )
        items = (
            await self.apify_client.dataset(run['defaultDatasetId']).list_items()
        ).items

        self.new_jobs = []
        for item in items:
            try:
                job = GreenhouseJob.model_validate(item)
                self.new_jobs.append(
                    JobListing(
                        job_id=job.job_id,
                        job_title=job.title,
                        firm=job.company_name,
                        url=job.job_url,
                        country=resolve_country(job.location_name),
                        location=job.location_name,
                    )
                )
            except Exception:
                continue
