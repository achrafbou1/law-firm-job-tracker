import asyncio
from collections import defaultdict

from airtable.client import AirtableClient
from airtable.models.law_firm import LawFirm
from airtable.models.role_category import RoleCategory
from factories import law_firm_factory
from mail.gmail import GmailService
from scrapers.base import BaseScraper
from settings import settings

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

scheduler = AsyncIOScheduler(
    timezone=pytz.timezone('America/New_York')
)


async def run_scraper(scraper_cls, urls, keywords):
    mail_service = GmailService(settings.sender_email, settings.sender_pass)
    airtable_client = AirtableClient()
    jobs_scraper = scraper_cls(urls=urls, keywords=keywords)
    await jobs_scraper.run()

    airtable_client.bulk_upsert_job_listings(
        jobs_scraper.relevant_jobs
    )

    email_body = mail_service.get_job_listings_summary(
        jobs_scraper.relevant_jobs
    )

    mail_service.send_jobs_email(
        to=[settings.sender_email, settings.debug_email],
        body=email_body,
    )


async def main():
    urls_by_type: dict[
        type[BaseScraper],
        list[str]
    ] = defaultdict(list)

    for law_firm in LawFirm.all():
        if law_firm.is_active:
            scraper = law_firm_factory(law_firm)
            urls_by_type[scraper].append(law_firm.careers_url)

    keywords = [kw.strip() for r in RoleCategory.all() for kw in r.ats_keywords.split(',') if kw.strip()]

    # Schedule each scraper type with staggered start times (12:00, 12:10, 12:20, etc.)
    for index, scraper in enumerate(urls_by_type):
        start_minute = (index * 10) % 60
        start_hour = 12 + (index * 10) // 60

        scheduler.add_job(
            run_scraper,
            CronTrigger(hour=start_hour, minute=start_minute, timezone='America/New_York'),
            args=(scraper, urls_by_type[scraper], keywords),
            id=f"{scraper.__name__}_scheduled"
        )

    scheduler.start()

    # Keep the scheduler running
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
