from croniter import croniter
from pydantic import BaseModel, Field, HttpUrl, field_validator


class LawFirm(BaseModel):
    active: bool = Field(..., alias="Active")
    careers_url: HttpUrl = Field(..., alias="Careers URL")
    law_firm_name: str = Field(..., alias="Law Firm Name")
    schedule: str = Field(..., alias="Schedule")

    @field_validator("schedule")
    def validate_cron(cls, v):
        if not croniter.is_valid(v):
            raise ValueError("Invalid cron expression")
        return v