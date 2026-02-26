from typing import Annotated, Any

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, field_validator

from src.settings import settings


def _default_pagination() -> int:
    return 1 if settings.is_dev else 0


class WorkdayInput(BaseModel):
    details: bool = True
    proxyUrls: dict[str, bool] = {'useApifyProxy': True}
    startUrls: list[dict[str, HttpUrl]] = Field(default_factory=list)
    stats: bool = False
    pagination: int = Field(default_factory=_default_pagination)

    @field_validator('startUrls', mode='before')
    @classmethod
    def normalize_start_urls(cls, v: Any) -> list[dict]:
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
    url: HttpUrl | EmptyStr | None = ''


class Metadata(BaseModel):
    originUrl: HttpUrl | None = None
    stats: dict[str, Any] = Field(default_factory=dict)


class WorkdayJob(BaseModel):
    canApply: bool
    country: str = ''
    hiringOrganization: HiringOrganization | None = None
    id: str
    jobDescription: str = ''
    location: str = ''
    metadata: Metadata
    postedOn: str = ''
    similarJobs: list[Any] = Field(default_factory=list)
    startDate: str = ''
    timeType: str = ''
    title: str = ''
    url: HttpUrl
