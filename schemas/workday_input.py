from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator, Field


class WorkdayInput(BaseModel):
    details: bool = True
    proxyUrls: dict[str, bool] = {"useApifyProxy": True}
    startUrls: list[dict[str, HttpUrl]] = Field(default_factory=list)
    stats: bool = False
    pagination: int = 0

    @field_validator("startUrls", mode="before")
    @classmethod
    def handle_single_url(cls, v: Any):
        # If user passes a single string → convert to list of dicts
        if isinstance(v, str):
            return [{"url": v}]
        return v