from scrapers.base import BaseScraper
from scrapers.workday.scraper import WorkdayScraper
from airtable.schemas import LawFirm


def law_firm_factory(law_firm: LawFirm) -> type[BaseScraper]:
    if 'myworkdayjobs.com' in law_firm.careers_url.host:
        return WorkdayScraper
    raise ValueError('Unsupported law firm type')
