"""Integration tests for the SmartRecruiters scraper with mocked Apify."""
import asyncio
from unittest.mock import patch

import pytest

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.smartrecruiters import SmartRecruitersScraper


@pytest.fixture
def mock_smartrecruiters_response():
    return [
        {
            'title': 'Legal Secretary',
            'description': 'Legal secretary position...',
            'requirements': 'Required qualifications...',
            'location': 'New York, NY',
            'department': 'Legal',
            'job_type': 'Full-time',
            'salary': 'N/A',
            'posted_date': '2026-01-15',
            'job_id': '744000112043001',
            'url': 'https://jobs.smartrecruiters.com/TestFirm/744000112043001-legal-secretary',
            'company': 'jobs.smartrecruiters.com',
            'source': 'SmartRecruiters',
        },
        {
            'title': 'Paralegal',
            'description': 'Paralegal position...',
            'requirements': 'Paralegal certificate...',
            'location': 'Chicago, IL',
            'department': 'Legal',
            'job_type': 'Full-time',
            'salary': '55000',
            'posted_date': '2026-01-16',
            'job_id': '744000112043002',
            'url': 'https://jobs.smartrecruiters.com/TestFirm/744000112043002-paralegal',
            'company': 'jobs.smartrecruiters.com',
            'source': 'SmartRecruiters',
        },
        {
            'title': 'Office Manager',
            'description': 'Office manager role...',
            'requirements': 'Management experience...',
            'location': 'N/A',
            'department': 'N/A',
            'job_type': 'N/A',
            'salary': 'N/A',
            'posted_date': 'N/A',
            'job_id': '744000112043003',
            'url': 'https://jobs.smartrecruiters.com/TestFirm/744000112043003-office-manager',
            'company': 'jobs.smartrecruiters.com',
            'source': 'SmartRecruiters',
        },
    ]
class TestSmartRecruitersScraperIntegration:
    def test_get_new_jobs_parses_response(self, mock_smartrecruiters_response, mock_apify_client):
        client = mock_apify_client(items=mock_smartrecruiters_response)
        scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
        scraper.apify_client = client
        asyncio.run(scraper.get_new_jobs())
        client.actor.assert_called_once_with(SmartRecruitersScraper.ACTOR_ID)
        assert len(scraper.new_jobs) == 3
        job_titles = {j.job_title for j in scraper.new_jobs}
        assert 'Legal Secretary' in job_titles
        assert 'Paralegal' in job_titles
        assert 'Office Manager' in job_titles
    def test_get_new_jobs_extracts_company(self, mock_smartrecruiters_response, mock_apify_client):
        client = mock_apify_client(items=mock_smartrecruiters_response)
        scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
        scraper.apify_client = client
        asyncio.run(scraper.get_new_jobs())
        assert all(j.firm == 'jobs.smartrecruiters.com' for j in scraper.new_jobs)
    def test_get_new_jobs_sets_location(self, mock_smartrecruiters_response, mock_apify_client):
        client = mock_apify_client(items=mock_smartrecruiters_response)
        scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
        scraper.apify_client = client
        asyncio.run(scraper.get_new_jobs())
        secretary = next(j for j in scraper.new_jobs if j.job_title == 'Legal Secretary')
        assert secretary.location == 'New York, NY'
    def test_get_new_jobs_sets_job_id(self, mock_smartrecruiters_response, mock_apify_client):
        client = mock_apify_client(items=mock_smartrecruiters_response)
        scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
        scraper.apify_client = client
        asyncio.run(scraper.get_new_jobs())
        job_ids = {j.job_id for j in scraper.new_jobs}
        assert '744000112043001' in job_ids
        assert '744000112043002' in job_ids
        assert '744000112043003' in job_ids
    def test_full_scrape_workflow(self, mock_smartrecruiters_response, mock_apify_client):
        client = mock_apify_client(items=mock_smartrecruiters_response)
        with patch.object(JobListing, 'all', return_value=[]):
            scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
            scraper.apify_client = client
            jobs = asyncio.run(scraper.run())
            assert all(job.status == 'NEW' for job in jobs)
            assert len(jobs) == 3
    def test_get_new_jobs_handles_invalid_item(self, mock_apify_client):
        items = [
            {'title': 'Good Job', 'job_id': '001', 'url': 'https://example.com/1'},
            {'title': 'Bad Job'},
            {'title': 'Another Good', 'job_id': '003', 'url': 'https://example.com/3'},
        ]
        client = mock_apify_client(items=items)
        scraper = SmartRecruitersScraper(urls=['https://careers.smartrecruiters.com/TestFirm'])
        scraper.apify_client = client
        asyncio.run(scraper.get_new_jobs())
        assert len(scraper.new_jobs) == 2
class TestSmartRecruitersDiffCheck:
    def test_diff_check_with_mixed_statuses(self):
        def make_job(job_id):
            return JobListing(
                job_id=job_id, job_title='Test', firm='Firm',
                url=f"https://example.com/{job_id}",
                location='NY', country='',
            )
        scraper = SmartRecruitersScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B'), make_job('C')]
        scraper.new_jobs = [make_job('B'), make_job('C'), make_job('D')]
        result = scraper.diff_check()
        statuses = {j.job_id: j.status for j in result}
        assert statuses['A'] == 'CLOSED'
        assert statuses['B'] == 'OLD'
        assert statuses['C'] == 'OLD'
        assert statuses['D'] == 'NEW'
    def test_diff_check_sets_first_seen(self):
        scraper = SmartRecruitersScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = [JobListing(
            job_id='NEW-1', job_title='New', firm='F',
            url='https://example.com/new', location='NY', country='',
        )]
        result = scraper.diff_check()
        assert next(j for j in result if j.job_id == 'NEW-1').first_seen is not None
    def test_diff_check_sets_last_seen(self):
        scraper = SmartRecruitersScraper(urls=[])
        scraper.previous_jobs = [JobListing(
            job_id='OLD-1', job_title='Old', firm='F',
            url='https://example.com/old', location='NY', country='',
        )]
        scraper.new_jobs = []
        result = scraper.diff_check()
        assert next(j for j in result if j.job_id == 'OLD-1').last_seen is not None
