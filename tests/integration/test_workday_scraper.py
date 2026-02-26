"""Integration tests for the Workday scraper with mocked Apify."""

import asyncio
from unittest.mock import patch

import pytest

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.workday import WorkdayScraper


@pytest.fixture
def mock_apify_response():
    """Sample Apify actor response data."""
    return [
        {
            'canApply': True,
            'country': 'United States of America',
            'hiringOrganization': {'name': 'Test Law Firm', 'url': ''},
            'id': 'JOB-001',
            'jobDescription': 'Associate position',
            'location': 'New York, NY',
            'metadata': {'originUrl': None, 'stats': {}},
            'postedOn': '2024-01-15',
            'similarJobs': [],
            'startDate': '',
            'timeType': 'Full-time',
            'title': 'Associate Attorney',
            'url': 'https://example.com/job/001'
        },
        {
            'canApply': True,
            'country': 'United States of America',
            'hiringOrganization': {'name': 'Test Law Firm', 'url': ''},
            'id': 'JOB-002',
            'jobDescription': 'Paralegal position',
            'location': 'Chicago, IL',
            'metadata': {'originUrl': None, 'stats': {}},
            'postedOn': '2024-01-16',
            'similarJobs': [],
            'startDate': '',
            'timeType': 'Full-time',
            'title': 'Senior Paralegal',
            'url': 'https://example.com/job/002'
        }
    ]


class TestWorkdayScraperIntegration:
    def test_get_new_jobs_parses_apify_response(self, mock_apify_response, mock_apify_client):
        """Test that get_new_jobs correctly parses Apify actor response."""
        client = mock_apify_client(items=mock_apify_response)

        scraper = WorkdayScraper(urls=['https://example.workday.com/jobs'])
        scraper.apify_client = client

        asyncio.run(scraper.get_new_jobs())

        client.actor.assert_called_once_with(WorkdayScraper.ACTOR_ID)
        assert len(scraper.new_jobs) == 2

    def test_full_scrape_workflow_with_mocks(self, mock_apify_response, mock_apify_client):
        """Test the full scrape workflow with all external services mocked."""
        client = mock_apify_client(items=mock_apify_response)

        with patch.object(JobListing, 'all', return_value=[]):
            scraper = WorkdayScraper(urls=['https://example.workday.com/jobs'])
            scraper.apify_client = client

            jobs = asyncio.run(scraper.run())

            assert all(job.status == 'NEW' for job in jobs)
            assert len(jobs) == 2


class TestWorkdayScraperDiffCheck:
    def test_diff_check_with_mixed_statuses(self):
        """Test diff_check correctly identifies NEW, OLD, and CLOSED jobs."""
        def make_job(job_id: str) -> JobListing:
            return JobListing(
                job_id=job_id,
                job_title='Test Job',
                firm='Test Firm',
                url=f'https://example.com/job/{job_id}',
                location='New York',
                country='USA',
            )

        # Previous: A, B, C
        # New: B, C, D
        # Expected: A=CLOSED, B=OLD, C=OLD, D=NEW
        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B'), make_job('C')]
        scraper.new_jobs = [make_job('B'), make_job('C'), make_job('D')]

        result = scraper.diff_check()
        statuses = {job.job_id: job.status for job in result}

        assert statuses['A'] == 'CLOSED'
        assert statuses['B'] == 'OLD'
        assert statuses['C'] == 'OLD'
        assert statuses['D'] == 'NEW'

    def test_diff_check_sets_first_seen_for_new_jobs(self):
        """Test that first_seen is set for NEW jobs."""
        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = [
            JobListing(
                job_id='NEW-001',
                job_title='New Job',
                firm='Test Firm',
                url='https://example.com/job/new',
                location='NYC',
                country='USA',
            )
        ]

        result = scraper.diff_check()

        new_job = next(j for j in result if j.job_id == 'NEW-001')
        assert new_job.first_seen is not None

    def test_diff_check_sets_last_seen_for_closed_jobs(self):
        """Test that last_seen is set for CLOSED jobs."""
        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = [
            JobListing(
                job_id='OLD-001',
                job_title='Old Job',
                firm='Test Firm',
                url='https://example.com/job/old',
                location='NYC',
                country='USA',
            )
        ]
        scraper.new_jobs = []

        result = scraper.diff_check()

        closed_job = next(j for j in result if j.job_id == 'OLD-001')
        assert closed_job.last_seen is not None
