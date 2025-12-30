import csv
import inspect
from pathlib import Path

from airtable.models.job_listing import JobListing
from mail.gmail import GmailService
from scrapers.workday.scraper import WorkdayScraper
from settings import settings


def test_status_update__success():
    inspect.signature(JobListing.__init__).parameters

    with open('tests/data/old_workdayjobs.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        old_jobs = list(reader)
        old_jobs = [JobListing(job_id=job['id'],
                                     job_title=job['title'],
                                     firm=job['hiringOrganization/name'], url=job['url']) for job in old_jobs]

    with open('tests/data/new_workdayjobs.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        new_jobs = list(reader)
        new_jobs = [JobListing(job_id=job['id'],
                               job_title=job['title'],
                               firm=job['hiringOrganization/name'], url=job['url']) for job in new_jobs]

    scraper = WorkdayScraper(urls=[])
    scraper.previous_jobs = old_jobs
    scraper.new_jobs = new_jobs
    scraper.diff_check()

    mail_service = GmailService(settings.sender_email, settings.sender_pass)
    template = Path('mail/job_updates_email.html').read_text(encoding='utf-8')
    job_items_html = ''.join(
        f"""
        <div style="margin-bottom: 16px; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
          <p style="margin: 0 0 6px;"><strong>{listing.job_title}</strong></p>
          <p style="margin: 0;">Job ID: {listing.job_id}</p>
          <p style="margin: 0;">Status: <strong>{listing.status}</strong></p>
          <p style="margin: 6px 0 0;">
            <a href="{listing.url}" target="_blank">View Job</a>
          </p>
        </div>
        """
        for listing in scraper.all_jobs
        if listing.status in {'NEW', 'CLOSED'}
    )
    email_body = template.replace(
        '<!-- JOB_ITEMS_START -->\n    <!-- JOB_ITEMS_END -->',
        job_items_html
    )
    mail_service.send(settings.sender_email, 'Test Job Listings', email_body)
    print()
