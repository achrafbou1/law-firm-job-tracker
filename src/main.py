import argparse
import asyncio
import os
from collections import defaultdict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from src.constants import TARGET_COUNTRY, TIMEZONE
from src.exceptions import UnsupportedATSType
from src.factories import law_firm_factory
from src.services.airtable.client import AirtableClient
from src.services.airtable.models.law_firm import LawFirm
from src.services.airtable.models.role_category import RoleCategory
from src.services.email.service import SendGridEmailService
from src.services.scrapers.base import BaseScraper
from src.services.scrapers.filters import filter_by_country, filter_by_keywords, filter_by_status

scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def run_scraper(
    scraper_cls: type[BaseScraper],
    urls: list[str],
    keywords: list[str],
    email_service: SendGridEmailService,
    airtable_client: AirtableClient,
) -> None:
    jobs_scraper = scraper_cls(urls=urls)
    logger.info('Running scraper for ATS type: {} with {} URLs', scraper_cls.__name__, len(urls))
    all_jobs = await jobs_scraper.run()

    # Persist every job (NEW, OLD, CLOSED) so statuses are tracked correctly
    logger.info('Upserting {} job listings in Airtable for ATS type: {}',
                len(all_jobs),
                scraper_cls.__name__)
    airtable_client.bulk_upsert_job_listings(all_jobs)
    logger.info('Job listings upserted for ATS type: {}', scraper_cls.__name__)

    # Filter pipeline – only email genuinely new or newly-closed jobs
    relevant_jobs = filter_by_status(all_jobs, {'NEW', 'CLOSED'})
    relevant_jobs = filter_by_keywords(relevant_jobs, keywords)
    relevant_jobs = filter_by_country(relevant_jobs, TARGET_COUNTRY)

    if not relevant_jobs:
        logger.info('No new or closed jobs to report for ATS type: {}, skipping email',
                    scraper_cls.__name__)
        return

    logger.info('Sending email for ATS type: {}', scraper_cls.__name__)
    email_body = email_service.get_job_listings_summary(relevant_jobs)
    email_service.send_jobs_email(body=email_body, ats=scraper_cls.__name__)
    logger.info('Mailed {} job listings for ATS type: {}', len(relevant_jobs), scraper_cls.__name__)


async def main(run_once: bool = False) -> None:
    urls_by_type: dict[type[BaseScraper], list[str]] = defaultdict(list)

    email_service = SendGridEmailService()
    airtable_client = AirtableClient()

    logger.info('Fetching active law firms from Airtable...')
    for law_firm in LawFirm.all():
        if law_firm.is_active:
            try:
                scraper = law_firm_factory(law_firm)
                urls_by_type[scraper].append(law_firm.careers_url)
            except UnsupportedATSType:
                logger.warning('Unsupported ATS type for law firm: {}, skipping..', law_firm.name)

    logger.info('Fetching keywords list from Airtable...')
    keywords = [
        kw.strip()
        for r in RoleCategory.all()
        for kw in r.ats_keywords.split(',')
        if kw.strip()
    ]

    if run_once:
        logger.info('Running one-shot scraping...')
        tasks = [
            run_scraper(scraper, urls_by_type[scraper], keywords, email_service, airtable_client)
            for scraper in urls_by_type
        ]
        await asyncio.gather(*tasks)
        logger.info('One-shot run complete.')
        return

    # Schedule each scraper type with staggered start times
    for index, scraper in enumerate(urls_by_type):
        start_minute = (index * 10) % 60
        start_hour = 12 + (index * 10) // 60

        logger.info(
            'Added scheduled job for ATS type: {} at {:02d}:{:02d}',
            scraper.__name__, start_hour, start_minute,
        )
        scheduler.add_job(
            run_scraper,
            CronTrigger(hour=start_hour, minute=start_minute, timezone=TIMEZONE),
            args=(scraper, urls_by_type[scraper], keywords, email_service, airtable_client),
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
