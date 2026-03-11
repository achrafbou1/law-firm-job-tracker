
from src.exceptions import UnsupportedATSType
from src.services.airtable.models.law_firm import AtsType, LawFirm
from src.services.scrapers.ats.smartrecruiters import SmartRecruitersScraper
from src.services.scrapers.base import BaseScraper

SCRAPER_REGISTRY: dict[AtsType, type[BaseScraper]] = {
    # AtsType.WORKDAY: WorkdayScraper,
    # AtsType.GREENHOUSE: GreenhouseScraper,
    AtsType.SMARTRECRUITERS: SmartRecruitersScraper,
}


def law_firm_factory(law_firm: LawFirm) -> type[BaseScraper]:
    scraper = SCRAPER_REGISTRY.get(law_firm.ats_type)
    if scraper is None:
        raise UnsupportedATSType(
            f'Unsupported ATS type: {law_firm.ats_type!r}'
            f' for firm {law_firm.name!r}'
        )
    return scraper
