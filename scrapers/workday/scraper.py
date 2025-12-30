
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
                                     firm=job.hiringOrganization.name, url=str(job.url)) for job in raw_jobs]

    def get_previous_jobs(self):
        for url in self.urls:
            formula = f"FIND('{url}', {{Job URL}}) > 0"
            self.previous_jobs += JobListing.all(formula=formula)

    def diff_check(self):
        # Build sets of job_ids for quick membership tests
        new_ids = {j.job_id for j in self.new_jobs if getattr(j, 'job_id', None)}
        prev_ids = {j.job_id for j in self.previous_jobs if getattr(j, 'job_id', None)}

        # For each new job: if it existed before -> OLD, else -> NEW
        for job in self.new_jobs:
            if job.job_id in prev_ids:
                job.status = Status.OLD.value
            else:
                job.status = Status.NEW.value

        # For each previous job that no longer appears in new jobs -> CLOSED
        for job in self.previous_jobs:
            if job.job_id not in new_ids:
                job.status = Status.CLOSED.value

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
        self.all_jobs = list(merged.values())
