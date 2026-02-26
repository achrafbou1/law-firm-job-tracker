from abc import ABC, abstractmethod

from src.services.airtable.models.job_listing import JobListing


class EmailProvider(ABC):
    @abstractmethod
    def send_jobs_email(self, body: str) -> None:
        ...

    @abstractmethod
    def get_job_listings_summary(self, job_listings: list[JobListing]) -> str:
        ...
