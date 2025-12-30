import asyncio
from collections import defaultdict

from airtable.models.law_firm import LawFirm
from factories import law_firm_factory
from mail.gmail import GmailService
from scrapers.base import BaseScraper
from settings import settings

async def main():
    urls_by_type: dict[type[BaseScraper], list[str]] = defaultdict(list)
    mail_service = GmailService(settings.sender_email, settings.sender_pass)
    for law_firm in LawFirm.all():
        scraper = law_firm_factory(law_firm)
        urls_by_type[scraper].append(str(law_firm.careers_url))

    for scraper in urls_by_type:
        await scraper(urls_by_type[scraper]).run()
        mail_service.send(settings.sender_email, 'New Job Listings', str(scraper.all_jobs))





if __name__ == '__main__':
    asyncio.run(main())
