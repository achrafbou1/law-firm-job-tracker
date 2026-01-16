import asyncio
from collections import defaultdict

from airtable.client import AirtableClient
from airtable.models.law_firm import LawFirm
from airtable.models.role_category import RoleCategory
from factories import law_firm_factory
from mail.gmail import GmailService
from scrapers.base import BaseScraper
from settings import settings


async def main():
    urls_by_type: dict[
        type[BaseScraper],
        list[str]
    ] = defaultdict(list)
    mail_service = GmailService(settings.sender_email, settings.sender_pass)
    airtable_client = AirtableClient()
    for law_firm in LawFirm.all():
        if law_firm.is_active:
            scraper = law_firm_factory(law_firm)
            urls_by_type[scraper].append(law_firm.careers_url)

    keywords = [kw.strip() for r in RoleCategory.all() for kw in r.ats_keywords.split(',') if kw.strip()]

    for scraper in urls_by_type:
        jobs_scraper = scraper(urls=urls_by_type[scraper], keywords=keywords)
        await jobs_scraper.run()

        # Save new jobs to Airtable
        airtable_client.bulk_upsert_job_listings(jobs_scraper.relevant_jobs)

        email_body = mail_service.get_job_listings_summary(jobs_scraper.relevant_jobs)
        mail_service.send_jobs_email(to=[settings.sender_email, settings.debug_email], body=email_body)






if __name__ == '__main__':
    asyncio.run(main())
