"""Unit tests for the ApifyScraper base class."""

from datetime import datetime
from unittest.mock import patch

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.base import ApifyScraper


def make_job(job_id: str, status: str = None) -> JobListing:
    """Create a minimal JobListing for testing."""
    job = JobListing(
        job_id=job_id,
        job_title='Test Job',
        firm='Test Firm',
        url=f'https://example.com/jobs/{job_id}',
        location='New York',
        country='USA',
    )
    if status:
        job.status = status
    return job


class ConcreteApifyScraper(ApifyScraper):
    """Concrete implementation for testing."""
    ACTOR_ID = 'test/actor'

    async def get_new_jobs(self) -> None:
        # Mock implementation - jobs would be set externally in tests
        pass


class TestApifyScraperDiffCheck:
    def test_new_jobs_get_new_status(self):
        """Test that jobs not in previous get NEW status."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B')]
        scraper.new_jobs = [make_job('B'), make_job('C')]

        result = scraper.diff_check()
        statuses = {j.job_id: j.status for j in result}

        assert statuses['C'] == 'NEW'

    def test_old_jobs_get_old_status(self):
        """Test that jobs in both lists get OLD status."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B')]
        scraper.new_jobs = [make_job('A'), make_job('B')]

        result = scraper.diff_check()
        statuses = {j.job_id: j.status for j in result}

        assert statuses['A'] == 'OLD'
        assert statuses['B'] == 'OLD'

    def test_closed_jobs_get_closed_status(self):
        """Test that jobs only in previous get CLOSED status."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B')]
        scraper.new_jobs = [make_job('B')]

        result = scraper.diff_check()
        statuses = {j.job_id: j.status for j in result}

        assert statuses['A'] == 'CLOSED'

    def test_new_jobs_get_first_seen_date(self):
        """Test that NEW jobs get first_seen set."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = [make_job('NEW-001')]

        result = scraper.diff_check()
        new_job = next(j for j in result if j.job_id == 'NEW-001')

        assert new_job.first_seen is not None
        assert isinstance(new_job.first_seen, datetime)

    def test_closed_jobs_get_last_seen_date(self):
        """Test that CLOSED jobs get last_seen set."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('OLD-001')]
        scraper.new_jobs = []

        result = scraper.diff_check()
        closed_job = next(j for j in result if j.job_id == 'OLD-001')

        assert closed_job.last_seen is not None
        assert isinstance(closed_job.last_seen, datetime)

    def test_empty_previous_all_new(self):
        """Test that all jobs are NEW when no previous jobs."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = [make_job('A'), make_job('B'), make_job('C')]

        result = scraper.diff_check()

        assert all(j.status == 'NEW' for j in result)
        assert len(result) == 3

    def test_empty_new_all_closed(self):
        """Test that all jobs are CLOSED when no new jobs."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B')]
        scraper.new_jobs = []

        result = scraper.diff_check()

        assert all(j.status == 'CLOSED' for j in result)
        assert len(result) == 2


class TestApifyScraperMergeJobs:
    def test_merge_prefers_new_jobs(self):
        """Test that _merge_jobs prefers new job data over previous."""
        scraper = ConcreteApifyScraper(urls=[])

        old_job = make_job('A')
        old_job.job_title = 'Old Title'

        new_job = make_job('A')
        new_job.job_title = 'New Title'

        scraper.previous_jobs = [old_job]
        scraper.new_jobs = [new_job]

        result = scraper._merge_jobs()

        assert len(result) == 1
        assert result[0].job_title == 'New Title'

    def test_merge_includes_all_jobs(self):
        """Test that _merge_jobs includes jobs from both lists."""
        scraper = ConcreteApifyScraper(urls=[])
        scraper.previous_jobs = [make_job('A'), make_job('B')]
        scraper.new_jobs = [make_job('B'), make_job('C')]

        result = scraper._merge_jobs()
        job_ids = {j.job_id for j in result}

        assert job_ids == {'A', 'B', 'C'}
        assert len(result) == 3


class TestApifyScraperGetPreviousJobs:
    @patch.object(JobListing, 'all', autospec=True)
    def test_get_previous_jobs_queries_airtable(self, mock_all):
        """Test that get_previous_jobs queries Airtable for each URL."""
        mock_all.return_value = [make_job('JOB-1')]

        scraper = ConcreteApifyScraper(urls=[
            'https://example.com/jobs1',
            'https://example.com/jobs2'
        ])
        scraper.get_previous_jobs()

        assert mock_all.call_count == 2
        assert len(scraper.previous_jobs) == 2

    @patch.object(JobListing, 'all', autospec=True)
    def test_get_previous_jobs_uses_find_formula(self, mock_all):
        """Test that get_previous_jobs uses FIND formula with URL."""
        mock_all.return_value = []

        scraper = ConcreteApifyScraper(urls=['https://example.com/careers'])
        scraper.get_previous_jobs()

        call_args = mock_all.call_args
        assert 'formula' in call_args.kwargs
        assert 'https://example.com/careers' in call_args.kwargs['formula']
        assert 'FIND' in call_args.kwargs['formula']
