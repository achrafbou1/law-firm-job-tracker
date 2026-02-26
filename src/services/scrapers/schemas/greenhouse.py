"""Pydantic schemas for Greenhouse API responses (jupri/greenhouse actor)."""

from pydantic import BaseModel, Field, HttpUrl

from src.settings import settings


class GreenhouseInput(BaseModel):
    """Input schema for jupri/greenhouse Apify actor."""
    url: list[str] = Field(default_factory=list)
    limit: int = Field(default_factory=lambda: 10 if settings.is_dev else 100000000)
    dev_dataset_clear: bool = False
    dev_no_strip: bool = False

    @classmethod
    def from_urls(cls, urls: list[str]) -> 'GreenhouseInput':
        """Create input from a list of URL strings."""
        return cls(url=urls)


class GreenhouseLocation(BaseModel):
    """Location object returned by the Greenhouse API."""
    name: str = ''


class GreenhouseDepartment(BaseModel):
    """Department object returned by the Greenhouse API."""
    model_config = {'extra': 'ignore'}

    name: str = ''


class GreenhouseJob(BaseModel):
    """Schema for a job returned by jupri/greenhouse.

    Only the fields we actually use are declared; the rest are ignored
    via model_config.
    """
    model_config = {'extra': 'ignore'}

    id: int
    title: str = ''
    url: HttpUrl | None = None
    location: GreenhouseLocation | None = None
    company_name: str = ''
    department: GreenhouseDepartment | None = None

    @property
    def job_id(self) -> str:
        return str(self.id)

    @property
    def job_url(self) -> str:
        return str(self.url) if self.url else ''

    @property
    def location_name(self) -> str:
        return self.location.name if self.location else ''
