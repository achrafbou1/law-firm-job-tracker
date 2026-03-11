"""Pydantic schemas for SmartRecruiters API responses
(limitless_ornament/smart-recruiters-job-board-scraper actor)."""
from pydantic import BaseModel, HttpUrl


class SmartRecruitersInput(BaseModel):
    """Input schema for limitless_ornament/smart-recruiters-job-board-scraper.
    The actor accepts a single ``url`` string pointing to a SmartRecruiters
    careers page (e.g. https://careers.smartrecruiters.com/CompanyName).
    """
    url: str
class SmartRecruitersJob(BaseModel):
    """Schema for a job returned by the SmartRecruiters scraper.
    Only the fields we actually use are declared; the rest are ignored
    via model_config.
    """
    model_config = {'extra': 'ignore'}
    title: str = ''
    location: str = ''
    department: str = ''
    job_type: str = ''
    job_id: str
    url: HttpUrl | str = ''
    company: str = ''
    source: str = ''
    @property
    def job_url(self) -> str:
        return str(self.url) if self.url else ''
