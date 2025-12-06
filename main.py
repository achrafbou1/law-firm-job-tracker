import asyncio
from collections import defaultdict

from factories import law_firm_factory
from scrapers.base import BaseScraper
from settings import settings
from airtable.provider import AirtableClientProvider
from airtable.schemas import LawFirm

async def main():
    airtable_client = AirtableClientProvider()
    airtable_client = airtable_client.get_client()
    law_firms_table = airtable_client.table(settings.LAW_FIRM_DB_ID, settings.LAW_FIRMS_TABLE_ID)

    urls_by_type: dict[type[BaseScraper], list[str]] = defaultdict(list)
    for record in law_firms_table.all():
        law_firm = LawFirm.model_validate(record['fields'])
        scraper = law_firm_factory(law_firm)
        urls_by_type[scraper].append(str(law_firm.careers_url))

    for scraper in urls_by_type:
        new_jobs = scraper(urls_by_type[scraper]).run()
        old_jobs = airtable_client.get_jobs()

if __name__ == "__main__":
    asyncio.run(main())