"""Integration tests for the Greenhouse scraper with mocked Apify."""

import asyncio
from unittest.mock import patch

import pytest

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.greenhouse import GreenhouseScraper, resolve_country


@pytest.fixture
def mock_greenhouse_response():
    """Sample Apify actor response data for Greenhouse (jupri/greenhouse format)."""
    return [
        {
            'id': 4105348009,
            'title': 'Corporate M&A Associate',
            'url': 'https://job-boards.greenhouse.io/firm/jobs/4105348009',
            'location': {'name': 'New York, NY'},
            'company_name': 'Hughes Hubbard & Reed LLP',
            'department': {'id': 123, 'name': 'Corporate'},
            'content': '<p>Join our team...</p>',
            'compliance': [],
        },
        {
            'id': 4063813009,
            'title': 'Billing Coordinator',
            'url': 'https://job-boards.greenhouse.io/firm/jobs/4063813009',
            'location': {'name': 'Miami, FL'},
            'company_name': 'Hughes Hubbard & Reed LLP',
            'department': {'id': 456, 'name': 'Finance'},
            'content': '<p>We are looking for...</p>',
            'compliance': [],
        },
        {
            'id': 4088378009,
            'title': '2027 Summer Associate',
            'url': 'https://job-boards.greenhouse.io/firm/jobs/4088378009',
            'location': {'name': 'Washington, D.C.'},
            'company_name': 'Hughes Hubbard & Reed LLP',
            'department': {'id': 789, 'name': 'Legal'},
            'content': '<p>International opportunity...</p>',
            'compliance': [],
        },
    ]


class TestGreenhouseScraperIntegration:
    def test_get_new_jobs_parses_response(self, mock_greenhouse_response, mock_apify_client):
        """Test that get_new_jobs correctly parses Greenhouse API response."""
        client = mock_apify_client(items=mock_greenhouse_response)

        scraper = GreenhouseScraper(urls=['https://job-boards.greenhouse.io/firm'])
        scraper.apify_client = client

        asyncio.run(scraper.get_new_jobs())

        client.actor.assert_called_once_with(GreenhouseScraper.ACTOR_ID)
        assert len(scraper.new_jobs) == 3

        job_titles = {j.job_title for j in scraper.new_jobs}
        assert 'Corporate M&A Associate' in job_titles
        assert 'Billing Coordinator' in job_titles
        assert '2027 Summer Associate' in job_titles

    def test_get_new_jobs_extracts_firm_name(self, mock_greenhouse_response, mock_apify_client):
        """Test that company_name is used as the firm."""
        client = mock_apify_client(items=mock_greenhouse_response)

        scraper = GreenhouseScraper(urls=['https://job-boards.greenhouse.io/firm'])
        scraper.apify_client = client

        asyncio.run(scraper.get_new_jobs())

        assert all(j.firm == 'Hughes Hubbard & Reed LLP' for j in scraper.new_jobs)

    def test_get_new_jobs_sets_location(self, mock_greenhouse_response, mock_apify_client):
        """Test that location.name is used as the location."""
        client = mock_apify_client(items=mock_greenhouse_response)

        scraper = GreenhouseScraper(urls=['https://job-boards.greenhouse.io/firm'])
        scraper.apify_client = client

        asyncio.run(scraper.get_new_jobs())

        associate = next(j for j in scraper.new_jobs if j.job_title == 'Corporate M&A Associate')
        assert associate.location == 'New York, NY'

    def test_get_new_jobs_resolves_country(self, mock_greenhouse_response, mock_apify_client):
        """Test that country is resolved from location."""
        client = mock_apify_client(items=mock_greenhouse_response)

        scraper = GreenhouseScraper(urls=['https://job-boards.greenhouse.io/firm'])
        scraper.apify_client = client

        asyncio.run(scraper.get_new_jobs())

        # NY → united states of america
        associate = next(j for j in scraper.new_jobs if j.job_title == 'Corporate M&A Associate')
        assert associate.country == 'united states of america'

        # FL → united states of america
        billing = next(j for j in scraper.new_jobs if j.job_title == 'Billing Coordinator')
        assert billing.country == 'united states of america'

        # D.C. → united states of america
        summer = next(j for j in scraper.new_jobs if j.job_title == '2027 Summer Associate')
        assert summer.country == 'united states of america'

    def test_full_scrape_workflow(self, mock_greenhouse_response, mock_apify_client):
        """Test the full scrape workflow with all external services mocked."""
        client = mock_apify_client(items=mock_greenhouse_response)

        with patch.object(JobListing, 'all', return_value=[]):
            scraper = GreenhouseScraper(urls=['https://job-boards.greenhouse.io/firm'])
            scraper.apify_client = client

            jobs = asyncio.run(scraper.run())

            assert all(job.status == 'NEW' for job in jobs)
            assert len(jobs) == 3


class TestResolveCountry:
    def test_state_abbreviation_ny(self):
        assert resolve_country('New York, NY') == 'united states of america'

    def test_state_abbreviation_fl(self):
        assert resolve_country('Miami, FL') == 'united states of america'

    def test_state_abbreviation_only(self):
        assert resolve_country('NY') == 'united states of america'

    def test_dc_with_dots(self):
        assert resolve_country('Washington, D.C.') == 'united states of america'

    def test_full_country_name(self):
        expected = 'united kingdom of great britain and northern ireland'
        assert resolve_country('London, United Kingdom') == expected

    def test_country_code_us(self):
        assert resolve_country('New York, US') == 'united states of america'

    def test_fuzzy_usa(self):
        assert resolve_country('New York, USA') == 'united states of america'

    def test_fuzzy_uk(self):
        expected = 'united kingdom of great britain and northern ireland'
        assert resolve_country('London, UK') == expected

    def test_empty_string(self):
        assert resolve_country('') == ''

    def test_none(self):
        assert resolve_country(None) == ''

    def test_unknown_location(self):
        assert resolve_country('zzzzz') == ''

    def test_multi_part_location(self):
        assert resolve_country('Manhattan, New York, NY') == 'united states of america'

    def test_semicolon_separated_us_offices(self):
        """Test semicolon-separated multi-location strings."""
        location = 'Boston Office; New York Office; Washington DC Office'
        assert resolve_country(location) == 'united states of america'

    def test_single_city_office(self):
        """Test city name with Office suffix."""
        assert resolve_country('Boston Office') == 'united states of america'

    def test_known_us_city_without_state(self):
        """Test well-known US city without state abbreviation."""
        assert resolve_country('Chicago') == 'united states of america'

    def test_state_name_without_suffix(self):
        """Test full US state name."""
        assert resolve_country('New York') == 'united states of america'


class TestGreenhouseDiffCheck:
    def test_diff_check_with_mixed_statuses(self):
        def make_job(job_id: str) -> JobListing:
            return JobListing(
                job_id=job_id, job_title='Test', firm='Firm',
                url=f'https://example.com/{job_id}',
                location='NY', country='USA',
            )

        scraper = GreenhouseScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B'), make_job('C')]
        scraper.new_jobs = [make_job('B'), make_job('C'), make_job('D')]

        result = scraper.diff_check()
        statuses = {j.job_id: j.status for j in result}

        assert statuses['A'] == 'CLOSED'
        assert statuses['B'] == 'OLD'
        assert statuses['C'] == 'OLD'
        assert statuses['D'] == 'NEW'

    def test_diff_check_sets_first_seen(self):
        scraper = GreenhouseScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = [JobListing(
            job_id='NEW-1', job_title='New', firm='F',
            url='https://example.com/new', location='NY', country='USA',
        )]

        result = scraper.diff_check()
        assert next(j for j in result if j.job_id == 'NEW-1').first_seen is not None

    def test_diff_check_sets_last_seen(self):
        scraper = GreenhouseScraper(urls=[])
        scraper.previous_jobs = [JobListing(
            job_id='OLD-1', job_title='Old', firm='F',
            url='https://example.com/old', location='NY', country='USA',
        )]
        scraper.new_jobs = []

        result = scraper.diff_check()
        assert next(j for j in result if j.job_id == 'OLD-1').last_seen is not None
