from scrapers.base import BaseScraper
from scrapers.workday import WorkDay


def law_firm_factory(law_firm_website: str) -> BaseScraper :
    if 'myworkdayjobs.com' in law_firm_website:
        return WorkDay(law_firm_website)