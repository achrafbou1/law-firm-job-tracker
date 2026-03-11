"""Base class for Apify-based scrapers."""

from dataclasses import dataclass, field
from datetime import datetime

from apify_client import ApifyClientAsync

from src.constants import TIMEZONE
from src.services.airtable.models.job_listing import JobListing, Status
from src.services.scrapers.ats.apify_provider import ApifyClientProvider
from src.services.scrapers.base import BaseScraper


@dataclass
class ApifyScraper(BaseScraper):
    """Base class for scrapers that use Apify actors.

    Provides common functionality for:
    - Apify client management
    - Fetching previous jobs from Airtable
    - Diff checking (NEW, OLD, CLOSED status)
    - Merging job lists

    Subclasses must implement:
    - ACTOR_ID: The Apify actor identifier
    - get_new_jobs(): Fetch and parse jobs from the Apify actor
    """
    apify_client: ApifyClientAsync = field(
        default_factory=ApifyClientProvider.get_client
    )

    def get_previous_jobs(self) -> None:
        """Fetch previously stored jobs from Airtable based on URL matching.

        Already-CLOSED jobs are excluded so they won't be re-emailed on
        subsequent runs.
        """
        for url in self.urls:
            formula = f"AND(FIND('{url}', {{Job URL}}) > 0, {{Status}} != 'CLOSED')"
            self.previous_jobs += JobListing.all(formula=formula)

    def diff_check(self) -> list[JobListing]:
        """Compare new and previous jobs to determine status changes.

        - Jobs in new but not in previous: NEW
        - Jobs in both: OLD
        - Jobs in previous but not in new: CLOSED
        """
        today = datetime.now(TIMEZONE)

        new_ids = {j.job_id for j in self.new_jobs if getattr(j, 'job_id', None)}
        prev_ids = {j.job_id for j in self.previous_jobs if getattr(j, 'job_id', None)}

        for job in self.new_jobs:
            if job.job_id in prev_ids:
                job.status = Status.OLD.value
                job.last_seen = today
            else:
                job.status = Status.NEW.value
                job.first_seen = today

        for job in self.previous_jobs:
            if job.job_id not in new_ids:
                job.status = Status.CLOSED.value
                job.last_seen = today

        return self._merge_jobs()

    def _merge_jobs(self) -> list[JobListing]:
        """Merge previous and new jobs, preferring new job data."""
        merged: dict[str, JobListing] = {}

        for job in self.previous_jobs:
            merged[job.job_id] = job

        for job in self.new_jobs:
            merged[job.job_id] = job

        return list(merged.values())
