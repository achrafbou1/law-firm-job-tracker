from airtable.models.law_firm import LawFirm, AtsType
from scrapers.base import BaseScraper
from scrapers.workday.scraper import WorkdayScraper


def law_firm_factory(law_firm: LawFirm) -> type[BaseScraper]:
    if law_firm.ats_type == AtsType.WORKDAY:
        return WorkdayScraper
    raise ValueError('Unsupported ATS type')
