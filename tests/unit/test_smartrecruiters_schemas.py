"""Unit tests for SmartRecruiters Pydantic schemas."""
import pytest
from pydantic import ValidationError

from src.services.scrapers.schemas.smartrecruiters import SmartRecruitersInput, SmartRecruitersJob


class TestSmartRecruitersInput:
    def test_valid_url(self):
        inp = SmartRecruitersInput(url='https://careers.smartrecruiters.com/PilotCompany/')
        assert inp.url == 'https://careers.smartrecruiters.com/PilotCompany/'
    def test_url_required(self):
        with pytest.raises(ValidationError):
            SmartRecruitersInput()
class TestSmartRecruitersJob:
    def test_valid_job_parsing(self):
        job_data = {
            'title': 'Janitorial Maintenance',
            'description': 'Some description...',
            'requirements': 'Some requirements...',
            'location': 'New York, NY',
            'department': 'Facility Services',
            'job_type': 'Full-time',
            'salary': '$15',
            'posted_date': '2026-01-15',
            'job_id': '744000112043667',
            'url': 'https://jobs.smartrecruiters.com/PilotCompany/744000112043667-janitorial',
            'company': 'jobs.smartrecruiters.com',
            'source': 'SmartRecruiters',
        }
        job = SmartRecruitersJob.model_validate(job_data)
        assert job.job_id == '744000112043667'
        assert job.title == 'Janitorial Maintenance'
        assert job.location == 'New York, NY'
        assert job.company == 'jobs.smartrecruiters.com'
        assert job.source == 'SmartRecruiters'
    def test_job_url_property(self):
        job = SmartRecruitersJob.model_validate({
            'job_id': '123',
            'url': 'https://jobs.smartrecruiters.com/Company/123-title',
        })
        assert job.job_url == 'https://jobs.smartrecruiters.com/Company/123-title'
    def test_job_url_empty(self):
        job = SmartRecruitersJob.model_validate({'job_id': '123', 'url': ''})
        assert job.job_url == ''
    def test_minimal_fields(self):
        job = SmartRecruitersJob.model_validate({'job_id': '999'})
        assert job.job_id == '999'
        assert job.title == ''
        assert job.location == ''
        assert job.company == ''
    def test_missing_job_id_raises_error(self):
        with pytest.raises(ValidationError):
            SmartRecruitersJob.model_validate({'title': 'Some Job'})
    def test_extra_fields_ignored(self):
        job = SmartRecruitersJob.model_validate({
            'job_id': '456',
            'title': 'Test',
            'some_unknown_field': 'value',
            'another_field': 42,
        })
        assert job.job_id == '456'
        assert not hasattr(job, 'some_unknown_field')
    def test_na_location(self):
        job = SmartRecruitersJob.model_validate({'job_id': '789', 'location': 'N/A'})
        assert job.location == 'N/A'
