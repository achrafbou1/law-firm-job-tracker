"""Workday ATS scraper implementation."""

from src.services.airtable.models.job_listing import JobListing
from src.services.scrapers.ats.base import ApifyScraper
from src.services.scrapers.schemas.workday import WorkdayInput, WorkdayJob


class WorkdayScraper(ApifyScraper):
    """Scraper for Workday ATS job boards."""

    ACTOR_ID = 'gooyer.co/myworkdayjobs'

    async def get_new_jobs(self) -> None:
        """Fetch new jobs from Workday using Apify actor."""
        run_input = WorkdayInput(startUrls=self.urls)
        run = await self.apify_client.actor(self.ACTOR_ID).call(
            run_input=run_input.model_dump()
        )
        items = (
            await self.apify_client.dataset(run['defaultDatasetId']).list_items()
        ).items
        raw_jobs = [WorkdayJob.model_validate(item) for item in items]
        self.new_jobs = [
            JobListing(
                job_id=job.id,
                job_title=job.title,
                firm=job.hiringOrganization.name if job.hiringOrganization else None,
                url=str(job.url),
                country=job.country,
                location=job.location,
            )
            for job in raw_jobs
        ]
