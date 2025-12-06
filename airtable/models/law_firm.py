from pyairtable.orm import Model, fields as F
from pydantic import HttpUrl

from settings import settings


class LawFirm(Model):
    is_active = F.CheckboxField("Active")
    careers_url = F.SingleLinkField("Careers URL")
    law_firm_name =  F.TextField("Law Firm Name")
    schedule = F.TextField("Schedule")
    company = F.SingleLinkField("Company")

    class Meta:
        base_id = settings.LAW_FIRM_DB_ID
        api_key = settings.LAW_FIRMS_API_KEY