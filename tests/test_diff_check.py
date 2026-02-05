import csv
from datetime import datetime
from zoneinfo import ZoneInfo

from airtable.models.job_listing import JobListing
from mail.service import MailerSendService
from scrapers.workday.scraper import WorkdayScraper
from settings import settings


def test_status_update__success():
    with open('tests/data/old_workdayjobs.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        old_jobs = list(reader)
        old_jobs = [JobListing(job_id=job['id'],
                                     job_title=job['title'],
                                     firm=job['hiringOrganization/name'], url=job['url'], location=job['location']) for job in old_jobs]

    with open('tests/data/new_workdayjobs.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        new_jobs = list(reader)
        new_jobs = [JobListing(job_id=job['id'],
                               job_title=job['title'],
                               firm=job['hiringOrganization/name'], url=job['url'], location=job['location']) for job in new_jobs]

    scraper = WorkdayScraper(urls=[])
    scraper.previous_jobs = old_jobs
    scraper.new_jobs = new_jobs
    scraper.diff_check()

    mail_service = MailerSendService(settings.sender_email, settings.sender_pass)
    keywords = 'office manager, office administration, office administrator, firm administrator, legal administrator, administrative manager, operations manager office, office operations manager, director of administration, administrative director, director of office administration, director of operations office, facilities manager, office services manager, director of office services, workplace manager, workplace operations, facilities and office management, communications, communication coordinator, communications coordinator, communication specialist, communications specialist, communication manager, communications manager, senior communications, senior communication manager, communications senior manager, director of communications, communications director, associate director communications, assistant director communications, public relations, pr coordinator, pr specialist, pr manager, senior pr manager, director of public relations, internal communications, internal communication manager, director internal communications, external communications, corporate communications, strategic communications, events, events coordinator, events specialist, events manager, senior events manager, director of events, marketing communications, marcom, marketing and communications, billing, billing specialist, billing coordinator, senior billing specialist, senior billing coordinator, billing supervisor, billing manager, senior billing manager, billing director, director billing, legal billing, client billing, revenue billing, time and billing, billing operations, client account specialist, senior client account specialist, client account coordinator, client account manager, finance, finance manager, director of finance, director finance, financial analysis, manager of financial analysis, pricing analyst, pricing manager, pricing director, strategic pricing analyst, client value, client value analyst, client value manager, director client value, client accounting, client accounting coordinator, client accounting specialist, client accounting manager, director client accounting, director of revenue, revenue management, financial systems, manager financial systems, director of financial systems, business analytics, manager of business analytics, pricing operations, pricing ops, practice development, practice development coordinator, practice development specialist, practice development manager, senior practice development, practice development senior, practice development senior manager, senior manager practice development, director of practice development, practice development director, associate director practice development, assistant director practice development, marketing and practice development, client development practice, business development, business development coordinator, business development specialist, business development manager, senior business development, business development senior, business development senior manager, senior manager business development, director of business development, associate director business development, assistant director business development, marketing and business development, client development'
    keywords = [k.strip() for k in keywords.split(',')]
    email_body = mail_service.get_job_listings_summary(scraper.all_jobs, keywords)
    now = datetime.now(ZoneInfo('America/New_York'))
    subject = f"{now.month}/{now.day}/{now.strftime('%y')}"
    mail_service.send(settings.sender_email, f'📢 New Jobs {subject}', email_body)
    print()
