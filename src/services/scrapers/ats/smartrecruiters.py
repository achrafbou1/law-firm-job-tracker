"""SmartRecruiters ATS scraper implementation."""
from loguru import logger

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.base import ApifyScraper
from src.services.scrapers.schemas.smartrecruiters import SmartRecruitersInput, SmartRecruitersJob


class SmartRecruitersScraper(ApifyScraper):
    """Scraper for SmartRecruiters ATS job boards.
    The underlying Apify actor accepts a single URL per run, so
    get_new_jobs iterates over all configured URLs and aggregates
    the results.
    """
    ACTOR_ID = 'limitless_ornament/smart-recruiters-job-board-scraper'
    async def get_new_jobs(self) -> None:
        """Fetch new jobs from SmartRecruiters using Apify actor."""
        self.new_jobs = []
        for url in self.urls:
            run_input = SmartRecruitersInput(url=url)
            run = await self.apify_client.actor(self.ACTOR_ID).call(
                run_input=run_input.model_dump()
            )
            items = (
                await self.apify_client.dataset(run['defaultDatasetId']).list_items()
            ).items
            for item in items:
                try:
                    job = SmartRecruitersJob.model_validate(item)
                    self.new_jobs.append(
                        JobListing(
                            job_id=job.job_id,
                            job_title=job.title,
                            firm=job.company,
                            url=job.job_url,
                            country='',
                            location=job.location,
                        )
                    )
                except Exception:
                    logger.warning(
                        'Failed to parse SmartRecruiters job item: {}',
                        item.get('job_id', 'unknown'),
                    )
                    continue
