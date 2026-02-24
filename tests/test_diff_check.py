import csv
from unittest.mock import patch, create_autospec

from sendgrid import SendGridAPIClient

from airtable.models.job_listing import JobListing
from scrapers.filters import filter_by_status, filter_by_keywords, filter_by_country
from scrapers.workday.scraper import WorkdayScraper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_jobs_from_csv(path: str) -> list[JobListing]:
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [
            JobListing(
                job_id=row['id'],
                job_title=row['title'],
                firm=row['hiringOrganization/name'],
                url=row['url'],
                location=row['location'],
                country=row.get('country', ''),
            )
            for row in reader
        ]


def _make_job(job_id: str, title: str = '', country: str = '', status: str | None = None) -> JobListing:
    """Create a minimal JobListing for unit tests."""
    job = JobListing(
        job_id=job_id,
        job_title=title,
        firm='Test Firm',
        url=f'https://example.com/jobs/{job_id}',
        location='New York',
        country=country,
    )
    if status:
        job.status = status
    return job


# ---------------------------------------------------------------------------
# diff_check tests
# ---------------------------------------------------------------------------

class TestDiffCheck:
    def test_new_jobs_get_new_status(self):
        old_jobs = [_make_job('A'), _make_job('B')]
        new_jobs = [_make_job('B'), _make_job('C')]

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        statuses = {j.job_id: j.status for j in merged}
        assert statuses['C'] == 'NEW'

    def test_removed_jobs_get_closed_status(self):
        old_jobs = [_make_job('A'), _make_job('B')]
        new_jobs = [_make_job('B')]

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        statuses = {j.job_id: j.status for j in merged}
        assert statuses['A'] == 'CLOSED'

    def test_unchanged_jobs_get_old_status(self):
        old_jobs = [_make_job('A')]
        new_jobs = [_make_job('A')]

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        statuses = {j.job_id: j.status for j in merged}
        assert statuses['A'] == 'OLD'

    def test_all_jobs_have_status(self):
        old_jobs = _load_jobs_from_csv('tests/data/old_workdayjobs.csv')
        new_jobs = _load_jobs_from_csv('tests/data/new_workdayjobs.csv')

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        assert all(job.status is not None for job in merged)

    def test_csv_status_correctness(self):
        old_jobs = _load_jobs_from_csv('tests/data/old_workdayjobs.csv')
        new_jobs = _load_jobs_from_csv('tests/data/new_workdayjobs.csv')

        old_ids = {j.job_id for j in old_jobs}
        new_ids = {j.job_id for j in new_jobs}

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        for job in merged:
            if job.job_id in new_ids and job.job_id not in old_ids:
                assert job.status == 'NEW'
            elif job.job_id in old_ids and job.job_id not in new_ids:
                assert job.status == 'CLOSED'

    def test_empty_previous_jobs(self):
        new_jobs = [_make_job('A'), _make_job('B')]

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = []
        scraper.new_jobs = new_jobs
        merged = scraper.diff_check()

        assert all(j.status == 'NEW' for j in merged)
        assert len(merged) == 2

    def test_empty_new_jobs(self):
        old_jobs = [_make_job('A'), _make_job('B')]

        scraper = WorkdayScraper(urls=[])
        scraper.previous_jobs = old_jobs
        scraper.new_jobs = []
        merged = scraper.diff_check()

        assert all(j.status == 'CLOSED' for j in merged)
        assert len(merged) == 2


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

class TestFilters:
    def test_filter_by_status(self):
        jobs = [
            _make_job('1', status='NEW'),
            _make_job('2', status='OLD'),
            _make_job('3', status='CLOSED'),
        ]
        result = filter_by_status(jobs, {'NEW', 'CLOSED'})
        assert {j.job_id for j in result} == {'1', '3'}

    def test_filter_by_status_empty_set(self):
        jobs = [_make_job('1', status='NEW')]
        assert filter_by_status(jobs, set()) == []

    def test_filter_by_keywords_match(self):
        jobs = [
            _make_job('1', title='Office Manager'),
            _make_job('2', title='Software Engineer'),
            _make_job('3', title='Senior Office Administrator'),
        ]
        result = filter_by_keywords(jobs, ['manager', 'administrator'])
        assert {j.job_id for j in result} == {'1', '3'}

    def test_filter_by_keywords_case_insensitive(self):
        jobs = [_make_job('1', title='BILLING Specialist')]
        result = filter_by_keywords(jobs, ['billing'])
        assert len(result) == 1

    def test_filter_by_keywords_no_match(self):
        jobs = [_make_job('1', title='Software Engineer')]
        result = filter_by_keywords(jobs, ['billing', 'manager'])
        assert result == []

    def test_filter_by_country(self):
        jobs = [
            _make_job('1', country='United States of America'),
            _make_job('2', country='Canada'),
            _make_job('3', country='  united states of america  '),
        ]
        result = filter_by_country(jobs, 'united states of america')
        assert {j.job_id for j in result} == {'1', '3'}

    def test_filter_by_country_no_match(self):
        jobs = [_make_job('1', country='Canada')]
        result = filter_by_country(jobs, 'united states of america')
        assert result == []


# ---------------------------------------------------------------------------
# Email summary tests (no network calls)
# ---------------------------------------------------------------------------

class TestEmailSummary:
    @patch('mail.service.SendGridAPIClient')
    def test_get_job_listings_summary_renders_html(self, mock_sgc):
        from mail.service import MailerSendService

        service = MailerSendService()
        jobs = [_make_job('1', title='Office Manager', status='NEW')]
        html = service.get_job_listings_summary(jobs)

        assert 'Office Manager' in html
        assert 'Test Firm' in html
        assert 'NEW' in html
        assert 'View Job' in html
        assert 'https://example.com/jobs/1' in html

    @patch('mail.service.SendGridAPIClient')
    def test_get_job_listings_summary_multiple_jobs(self, mock_sgc):
        from mail.service import MailerSendService

        service = MailerSendService()
        jobs = [
            _make_job('1', title='Office Manager', status='NEW'),
            _make_job('2', title='Billing Specialist', status='CLOSED'),
        ]
        html = service.get_job_listings_summary(jobs)

        assert 'Office Manager' in html
        assert 'Billing Specialist' in html
        assert '#2e7d32' in html  # green for NEW
        assert '#c62828' in html  # red for CLOSED

    @patch('mail.service.SendGridAPIClient')
    def test_get_job_listings_summary_empty(self, mock_sgc):
        from mail.service import MailerSendService

        service = MailerSendService()
        html = service.get_job_listings_summary([])

        assert 'Job Updates' in html

    @patch('mail.service.SendGridAPIClient')
    def test_send_jobs_email_calls_sendgrid(self, mock_sgc_cls):
        from mail.service import MailerSendService

        mock_client = create_autospec(SendGridAPIClient, instance=True)
        mock_sgc_cls.return_value = mock_client

        service = MailerSendService()
        service.send_jobs_email(body='<html>test</html>')

        mock_client.send.assert_called_once()

    @patch('mail.service.SendGridAPIClient')
    def test_send_jobs_email_has_correct_sender_and_recipient(self, mock_sgc_cls):
        from mail.service import MailerSendService
        from settings import settings

        mock_client = create_autospec(SendGridAPIClient, instance=True)
        mock_sgc_cls.return_value = mock_client

        service = MailerSendService()
        service.send_jobs_email(body='<html>jobs</html>')

        mail_obj = mock_client.send.call_args[0][0]
        assert mail_obj.from_email.email == settings.sender_email
        assert any(
            to['email'] == settings.receiver_email
            for p in mail_obj.personalizations
            for to in p.tos
        )

    @patch('mail.service.SendGridAPIClient')
    def test_send_jobs_email_has_correct_subject(self, mock_sgc_cls):
        from mail.service import MailerSendService

        mock_client = create_autospec(SendGridAPIClient, instance=True)
        mock_sgc_cls.return_value = mock_client

        service = MailerSendService()
        service.send_jobs_email(body='<html>jobs</html>')

        mail_obj = mock_client.send.call_args[0][0]
        assert str(mail_obj.subject).startswith('📢 New Jobs')

    @patch('mail.service.SendGridAPIClient')
    def test_send_jobs_email_has_html_body(self, mock_sgc_cls):
        from mail.service import MailerSendService

        mock_client = create_autospec(SendGridAPIClient, instance=True)
        mock_sgc_cls.return_value = mock_client

        body = '<html><body>Job listings here</body></html>'
        service = MailerSendService()
        service.send_jobs_email(body=body)

        mail_obj = mock_client.send.call_args[0][0]
        contents = mail_obj.contents
        assert any(c.mime_type == 'text/html' and c.content == body for c in contents)
