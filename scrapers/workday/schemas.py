from typing import List, Dict, Optional, Any, Union, Annotated
from pydantic import BaseModel, HttpUrl, Field, field_validator, StringConstraints


class Input(BaseModel):
    details: bool = True
    proxyUrls: dict[str, bool] = {'useApifyProxy': True}
    startUrls: list[dict[str, HttpUrl]] = Field(default_factory=list)
    stats: bool = False
    pagination: int = 0

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

EmptyStr = Annotated[str, StringConstraints(max_length=0)]

class HiringOrganization(BaseModel):
    name: str
    url: Optional[Union[HttpUrl, EmptyStr]] = ''


class Metadata(BaseModel):
    originUrl: Optional[HttpUrl] = None
    stats: Dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    canApply: bool
    country: str
    hiringOrganization: HiringOrganization | None = None
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
