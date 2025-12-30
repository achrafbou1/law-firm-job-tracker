from enum import Enum

from pyairtable.orm import Model, fields as F

from settings import settings


class Status(str, Enum):
    NEW = 'NEW'
    CLOSED = 'CLOSED'
    OLD = 'OLD'

class JobListing(Model):
    job_id = F.SingleLineTextField('Job ID')
    job_title = F.SingleLineTextField('Job Title')
    firm = F.SingleLineTextField('Firm')
    url = F.UrlField('Job URL')
    role_categories = F.MultipleSelectField('Role Categories')
    status = F.SelectField('Status')
    first_seen = F.DateField('First Seen')
    last_seen = F.DateField('Last Seen')
    actioned = F.CheckboxField('Actioned')

    class Meta:
        base_id = settings.law_firm_db_id
        api_key = settings.airtable_token
        table_name = 'Job Listings'
