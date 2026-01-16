from datetime import datetime
from zoneinfo import ZoneInfo

from airtable.models.job_listing import JobListing, Status
from scrapers.apify.base import ApifyScraper
from scrapers.workday.schemas import Input, Job


class WorkdayScraper(ApifyScraper):
    async def get_new_jobs(self):
        run_input = Input(startUrls=self.urls)
        run = await self.apify_client.actor('kma98hS67qBkPC6ub').call(
            run_input=run_input.model_dump()
        )
        items = (
            await self.apify_client.dataset(run['defaultDatasetId']).list_items()
        ).items
        raw_jobs = [Job.model_validate(item) for item in items]
        self.new_jobs = [JobListing(job_id=job.id,
                                     job_title=job.title,
                                     firm=job.hiringOrganization.name if job.hiringOrganization else None,
                                    url=str(job.url),
                                    country=job.country,
                                    location=job.location) for job in raw_jobs]

    def get_previous_jobs(self):
        for url in self.urls:
            formula = f"FIND('{url}', {{Job URL}}) > 0"
            self.previous_jobs += JobListing.all(formula=formula)

    def diff_check(self):
        today = datetime.now(ZoneInfo('America/New_York'))
        # Build sets of job_ids for quick membership tests
        new_ids = {j.job_id for j in self.new_jobs if getattr(j, 'job_id', None)}
        prev_ids = {j.job_id for j in self.previous_jobs if getattr(j, 'job_id', None)}

        # For each new job: if it existed before -> OLD, else -> NEW
        for job in self.new_jobs:
            if job.job_id in prev_ids:
                job.status = Status.OLD.value
            else:
                job.status = Status.NEW.value
                job.first_seen = today

        # For each previous job that no longer appears in new jobs -> CLOSED
        for job in self.previous_jobs:
            if job.job_id not in new_ids:
                job.status = Status.CLOSED.value
                job.last_seen = today

        self.merge_jobs()

    def merge_jobs(self):
        merged = {}

        # Add previous jobs first
        for job in self.previous_jobs:
            merged[job.job_id] = job

        # Add / overwrite with new jobs
        for job in self.new_jobs:
            merged[job.job_id] = job

        # Return merged list
        self.relevant_jobs = list(merged.values())
        self.relevant_jobs = [listing for listing in self.relevant_jobs if listing.status in {'NEW', 'CLOSED'}
            and any(
        kw.lower() in ' '.join(listing.job_title.lower().split()).split()
        for kw in self.keywords
    ) and listing.country.strip().lower() == 'united states of america']
