import asyncio
import os
import argparse
from collections import defaultdict

from loguru import logger

from airtable.client import AirtableClient
from airtable.models.law_firm import LawFirm
from airtable.models.role_category import RoleCategory
from errors import UnsupportedATSType
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
    logger.info('Running scraper for ATS type: {} with {} URLs', scraper_cls.__name__, len(urls))
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
    logger.info('Mailed job listings for ATS type: {}', scraper_cls.__name__)


async def main(run_once: bool = False):
    urls_by_type: dict[
        type[BaseScraper],
        list[str]
    ] = defaultdict(list)

    logger.info('Fetching active law firms from Airtable...')
    for law_firm in LawFirm.all():
        if law_firm.is_active:
            try:
                scraper = law_firm_factory(law_firm)
                urls_by_type[scraper].append(law_firm.careers_url)
            except UnsupportedATSType:
                logger.warning('Unsupported ATS type for law firm: {}, skipping..', law_firm.name)

    logger.info('Fetching keywords list from Airtable...')
    keywords = [kw.strip() for r in RoleCategory.all() for kw in r.ats_keywords.split(',') if kw.strip()]

    if run_once:
        logger.info('Running one-shot scraping...')
        tasks = [run_scraper(scraper, urls_by_type[scraper], keywords) for scraper in urls_by_type]
        await asyncio.gather(*tasks)
        logger.info('One-shot run complete.')
        return

    # Schedule each scraper type with staggered start times
    for index, scraper in enumerate(urls_by_type):
        start_minute = (index * 10) % 60
        start_hour = 12 + (index * 10) // 60

        logger.info('Added scheduled job for ATS type: {} at {:02d}:{:02d}', scraper.__name__, start_hour, start_minute)
        scheduler.add_job(
            run_scraper,
            CronTrigger(hour=start_hour, minute=start_minute, timezone='America/New_York'),
            args=(scraper, urls_by_type[scraper], keywords),
            id=f"{scraper.__name__}_scheduled"
        )

    logger.info('Starting scheduler...')
    scheduler.start()

    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run scrapers once and exit')
    args = parser.parse_args()

    run_once = args.once or os.getenv('RUN_ONCE', '0') == '1'
    asyncio.run(main(run_once))
