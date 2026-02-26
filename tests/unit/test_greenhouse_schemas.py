"""Unit tests for Greenhouse Pydantic schemas."""


from src.services.scrapers.schemas.greenhouse import (
    GreenhouseDepartment,
    GreenhouseInput,
    GreenhouseJob,
    GreenhouseLocation,
)


class TestGreenhouseInput:
    def test_from_urls_creates_correct_format(self):
        """Test that from_urls populates the url list."""
        urls = ['https://job-boards.greenhouse.io/company1', 'https://job-boards.greenhouse.io/company2']
        input_schema = GreenhouseInput.from_urls(urls)
        assert input_schema.url == urls

    def test_empty_urls_allowed(self):
        input_schema = GreenhouseInput.from_urls([])
        assert input_schema.url == []

    def test_default_flags(self):
        input_schema = GreenhouseInput.from_urls([])
        assert input_schema.dev_dataset_clear is False
        assert input_schema.dev_no_strip is False

    def test_model_dump_matches_actor_input(self):
        data = GreenhouseInput.from_urls(['https://job-boards.greenhouse.io/firm']).model_dump()
        assert 'url' in data
        assert 'limit' in data
        assert 'dev_dataset_clear' in data
        assert 'dev_no_strip' in data


class TestGreenhouseLocation:
    def test_valid_location(self):
        loc = GreenhouseLocation(name='New York, NY')
        assert loc.name == 'New York, NY'

    def test_empty_default(self):
        loc = GreenhouseLocation()
        assert loc.name == ''


class TestGreenhouseDepartment:
    def test_valid_department(self):
        dept = GreenhouseDepartment(name='Corporate')
        assert dept.name == 'Corporate'

    def test_empty_default(self):
        dept = GreenhouseDepartment()
        assert dept.name == ''


class TestGreenhouseJob:
    def test_valid_job_parsing(self):
        """Test parsing a full Greenhouse job matching real actor output."""
        job_data = {
            'id': 4105348009,
            'title': 'Corporate M&A Associate',
            'url': 'https://job-boards.greenhouse.io/hugheshubbardreedllp/jobs/4105348009',
            'location': {'name': 'New York, NY'},
            'company_name': 'Hughes Hubbard & Reed LLP',
            'department': {'id': 123, 'name': 'Corporate'},
            # extra fields the actor returns — should be ignored
            'content': '<p>...</p>',
            'internal_job_id': 4072150009,
            'metadata': [],
            'compliance': [],
            'questions': [],
            'published_at': '2026-01-15T11:29:12-05:00',
        }
        job = GreenhouseJob.model_validate(job_data)

        assert job.job_id == '4105348009'
        assert job.title == 'Corporate M&A Associate'
        assert job.job_url == 'https://job-boards.greenhouse.io/hugheshubbardreedllp/jobs/4105348009'
        assert job.location_name == 'New York, NY'
        assert job.company_name == 'Hughes Hubbard & Reed LLP'
        assert job.department.name == 'Corporate'

    def test_department_as_dict(self):
        """Test that department dict with id/name/path is parsed correctly."""
        job = GreenhouseJob.model_validate({
            'id': 1,
            'department': {'id': 4014739009, 'name': 'Corporate', 'path': []},
        })
        assert job.department.name == 'Corporate'

    def test_department_null(self):
        job = GreenhouseJob(id=1, department=None)
        assert job.department is None

    def test_department_missing(self):
        job = GreenhouseJob(id=1)
        assert job.department is None

    def test_location_name_with_null_location(self):
        job = GreenhouseJob(id=1, location=None)
        assert job.location_name == ''

    def test_location_name_missing(self):
        job = GreenhouseJob(id=1)
        assert job.location_name == ''

    def test_job_url_empty_when_no_url(self):
        job = GreenhouseJob(id=1)
        assert job.job_url == ''

    def test_minimal_fields(self):
        job = GreenhouseJob(id=42)
        assert job.job_id == '42'
        assert job.title == ''
        assert job.company_name == ''

    def test_extra_fields_ignored(self):
        """Test that unknown fields from the API don't cause errors."""
        job = GreenhouseJob.model_validate({
            'id': 1,
            'questions': [{'required': True}],
            'education': 'education_required',
            'compliance': [{'type': 'eeoc'}],
            'requisition_id': 'REQ-001',
            'data_compliance': [{'type': 'gdpr'}],
            'demographic_questions': None,
            'pay_input_ranges': [],
            'is_featured': False,
            'language': 'en',
            'first_published': '2025-01-01',
            'offices': [{'name': 'NYC'}],
            'departments': [{'name': 'Legal'}],
        })
        assert job.job_id == '1'
