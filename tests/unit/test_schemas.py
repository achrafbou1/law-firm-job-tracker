"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.services.scrapers.schemas.workday import HiringOrganization, WorkdayInput, WorkdayJob


class TestWorkdayInput:
    def test_urls_as_strings_normalized_to_dicts(self):
        """Test that string URLs are normalized to dict format."""
        urls = ['https://example.com/jobs', 'https://another.com/careers']
        input_schema = WorkdayInput(startUrls=urls)

        assert len(input_schema.startUrls) == 2
        assert all(isinstance(u, dict) for u in input_schema.startUrls)
        assert str(input_schema.startUrls[0]['url']) == 'https://example.com/jobs'

    def test_urls_as_dicts_preserved(self):
        """Test that dict URLs are preserved as-is."""
        urls = [{'url': 'https://example.com/jobs'}]
        input_schema = WorkdayInput(startUrls=urls)

        assert str(input_schema.startUrls[0]['url']) == 'https://example.com/jobs'

    def test_invalid_url_raises_error(self):
        """Test that invalid URLs raise validation error."""
        with pytest.raises(ValidationError):
            WorkdayInput(startUrls=['not-a-valid-url'])

    def test_empty_urls_allowed(self):
        """Test that empty URL list is allowed."""
        input_schema = WorkdayInput(startUrls=[])
        assert input_schema.startUrls == []

    def test_default_values(self):
        """Test default values are set correctly."""
        input_schema = WorkdayInput(startUrls=[])
        assert input_schema.details is True
        assert input_schema.stats is False
        assert input_schema.proxyUrls == {'useApifyProxy': True}


class TestWorkdayJob:
    def test_valid_job_parsing(self):
        """Test parsing a valid job response."""
        job_data = {
            'canApply': True,
            'country': 'United States of America',
            'hiringOrganization': {'name': 'Test Firm', 'url': ''},
            'id': 'JOB-123',
            'jobDescription': 'Test description',
            'location': 'New York, NY',
            'metadata': {'originUrl': None, 'stats': {}},
            'postedOn': '2024-01-01',
            'similarJobs': [],
            'startDate': '',
            'timeType': 'Full-time',
            'title': 'Associate Attorney',
            'url': 'https://example.com/job/123'
        }
        job = WorkdayJob.model_validate(job_data)

        assert job.id == 'JOB-123'
        assert job.title == 'Associate Attorney'
        assert job.country == 'United States of America'
        assert job.hiringOrganization.name == 'Test Firm'

    def test_job_with_missing_optional_fields(self):
        """Test parsing job with minimal required fields."""
        job_data = {
            'canApply': False,
            'id': 'JOB-456',
            'metadata': {'stats': {}},
            'url': 'https://example.com/job/456'
        }
        job = WorkdayJob.model_validate(job_data)

        assert job.id == 'JOB-456'
        assert job.country == ''
        assert job.title == ''
        assert job.hiringOrganization is None

    def test_job_with_null_hiring_organization(self):
        """Test job parsing when hiringOrganization is null."""
        job_data = {
            'canApply': True,
            'id': 'JOB-789',
            'hiringOrganization': None,
            'metadata': {'stats': {}},
            'url': 'https://example.com/job/789'
        }
        job = WorkdayJob.model_validate(job_data)
        assert job.hiringOrganization is None


class TestHiringOrganization:
    def test_valid_organization(self):
        """Test valid hiring organization parsing."""
        org = HiringOrganization(name='Law Firm LLC', url='https://lawfirm.com')
        assert org.name == 'Law Firm LLC'

    def test_empty_url_allowed(self):
        """Test that empty string URL is allowed."""
        org = HiringOrganization(name='Test Firm', url='')
        assert org.url == ''
