"""Pure-function filters for post-processing scraped job listings."""

from airtable.models.job_listing import JobListing


def filter_by_status(jobs: list[JobListing], statuses: set[str]) -> list[JobListing]:
    """Keep only jobs whose status is in the given set."""
    return [job for job in jobs if job.status in statuses]


def filter_by_keywords(jobs: list[JobListing], keywords: list[str]) -> list[JobListing]:
    """Keep only jobs whose title contains at least one keyword (case-insensitive, whole-word)."""
    lower_keywords = {kw.lower() for kw in keywords}
    return [
        job for job in jobs
        if any(kw in job.job_title.lower().split() for kw in lower_keywords)
    ]


def filter_by_country(jobs: list[JobListing], country: str) -> list[JobListing]:
    """Keep only jobs whose country matches (case-insensitive, stripped)."""
    target = country.strip().lower()
    return [job for job in jobs if job.country.strip().lower() == target]
