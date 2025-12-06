from pyairtable import Api

from airtable.models.law_firm import LawFirm
from settings import settings


class AirtableClientProvider:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = Api(settings.AIRTABLE_TOKEN)
        return cls._client

    @staticmethod
    def get_law_firms() -> list[LawFirm]:
        return LawFirm.all()

    def get_jobs(self):
        return Job.all()