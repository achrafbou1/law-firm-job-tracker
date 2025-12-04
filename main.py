
from pyairtable import Api

from schemas.law_firm import LawFirm
from settings import settings

api = Api(settings.AIRTABLE_TOKEN)
law_firms_table = api.table(settings.LAW_FIRM_DB_ID, settings.LAW_FIRMS_TABLE_ID)

for page in law_firms_table.iterate():
    for record in page:
        law_firm = LawFirm.model_validate(record['fields'])
        print()