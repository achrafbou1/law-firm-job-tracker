"""Pure-function filters for post-processing scraped job listings."""

from loguru import logger

from src.services.airtable.models.job_listing import JobListing


def filter_by_status(jobs: list[JobListing], statuses: set[str]) -> list[JobListing]:
    """Keep only jobs whose status is in the given set."""
    result = [job for job in jobs if job.status in statuses]
    logger.debug('Filtered {} jobs to {} by status {}', len(jobs), len(result), statuses)
    return result


def filter_by_keywords(jobs: list[JobListing], keywords: list[str]) -> list[JobListing]:
    """Keep only jobs whose title contains at least one keyword (case-insensitive, whole-word)."""
    lower_keywords = {kw.lower() for kw in keywords}
    result = [
        job for job in jobs
        if any(kw in job.job_title.lower().split() for kw in lower_keywords)
    ]
    logger.debug('Filtered {} jobs to {} by keywords', len(jobs), len(result))
    return result


def filter_by_country(jobs: list[JobListing], country: str) -> list[JobListing]:
    """Keep jobs whose country matches, or whose country could not be resolved.

    Jobs with an empty/unresolved country are kept (benefit of the doubt).
    """
    target = country.strip().lower()
    result = [
        job for job in jobs
        if not job.country or not job.country.strip() or job.country.strip().lower() == target
    ]
    logger.debug('Filtered {} jobs to {} by country {}', len(jobs), len(result), country)
    return result
