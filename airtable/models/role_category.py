from pyairtable.orm import Model, fields as F

from settings import settings


class RoleCategory(Model):
    ats_keywords = F.TextField('ATS Search Keywords')

    class Meta:
        base_id = settings.law_firm_db_id
        api_key = settings.airtable_token
        table_name = 'Role Categories'
