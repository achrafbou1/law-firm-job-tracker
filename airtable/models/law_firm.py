from enum import Enum

from pyairtable.orm import Model, fields as F

from settings import settings

class AtsType(str, Enum):
    WORKDAY = 'Workday'

class LawFirm(Model):
    is_active = F.CheckboxField('Active')
    careers_url = F.UrlField('Careers URL')
    name = F.SingleLineTextField('Law Firm Name')
    ats_type = F.SelectField('ATS Type')
    schedule = F.SingleLineTextField('Schedule')
    last_checked = F.DateField('Last Checked')

    class Meta:
        base_id = settings.law_firm_db_id
        api_key = settings.airtable_token
        table_name = 'Law Firms'
