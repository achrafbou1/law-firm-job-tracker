from pyairtable import Api

from src.services.airtable.models.job_listing import JobListing
from src.settings import settings


class AirtableClient:
    def __init__(self):
        self.api = Api(settings.airtable_token)

    def bulk_upsert_job_listings(self, job_listings: list[JobListing]) -> None:
        table = self.api.table(settings.law_firm_db_id, 'Job Listings')
        records = [{k: v for k, v in jl.to_record().items() if k != 'id'} for jl in job_listings]
        table.batch_upsert(key_fields=['Job ID'], records=records)
