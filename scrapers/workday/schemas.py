from typing import List, Dict, Optional, Any
from pydantic import BaseModel, HttpUrl, Field, field_validator


class Input(BaseModel):
    details: bool = True
    proxyUrls: dict[str, bool] = {'useApifyProxy': True}
    startUrls: list[dict[str, HttpUrl]] = Field(default_factory=list)
    stats: bool = False
    pagination: int = 1

    @field_validator('startUrls', mode='before')
    @classmethod
    def normalize_start_urls(cls, v: Any):
        # Expecting a list of URLs (strings or dicts)
        if not isinstance(v, list):
            raise ValueError('startUrls must be a list')

        normalized = []
        for item in v:
            if isinstance(item, str):
                normalized.append({'url': item})
            elif isinstance(item, dict):
                normalized.append(item)
            else:
                raise ValueError(f"Invalid item in startUrls: {item}")

        return normalized


class HiringOrganization(BaseModel):
    name: str
    url: Optional[HttpUrl] = None  # url may be empty string


class Metadata(BaseModel):
    originUrl: Optional[HttpUrl] = None
    stats: Dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    canApply: bool
    country: str
    hiringOrganization: HiringOrganization
    id: str
    jobDescription: str
    location: str
    metadata: Metadata
    postedOn: str
    similarJobs: List[Any] = Field(default_factory=list)
    startDate: str
    timeType: str
    title: str
    url: HttpUrl
