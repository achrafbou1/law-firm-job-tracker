from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

from mailersend import MailerSendClient, EmailBuilder, MailerSendError, RateLimitExceeded, ServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from airtable.models.job_listing import JobListing
from mail.provider import EmailProvider
from settings import settings


class MailerSendService(EmailProvider):
    _client: MailerSendClient

    def __init__(self):
        self._client = MailerSendClient(api_key=settings.mailersend_api_key)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((
                MailerSendError,
                ServerError,
                RateLimitExceeded,
        ))
    )
    def send_jobs_email(
            self,
            body: str
    ) -> None:

        now = datetime.now(ZoneInfo('America/New_York'))
        subject = f'📢 New Jobs {now.month}/{now.day}/{now.strftime('%y')}'

        email = (EmailBuilder()
        .from_email(settings.sender_email, 'Law Firm Jobs Monitor')
        .to(settings.receiver_email)
        .subject(subject)
        .html(body)
        .build())

        response = self._client.emails.send(email)

        if not response.success:
            status_code = response.status_code
            error_details = response.data
            raise MailerSendError(f'Failed to send email, status code: {status_code}, details: {error_details}')


    def _build_message(self, to: list[str], subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.username
        to = [addr for addr in to if addr and addr.strip()]
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        return msg

    @staticmethod
    def get_job_listings_summary(job_listings: list[JobListing]) -> str:
        template = Path('mail/job_updates_email.html').read_text(encoding='utf-8')
        job_items_html = ''.join(
            f"""
                <div style="margin-bottom: 16px; padding: 12px; border: 1px solid #ddd; border-radius: 6px;">
                    <p style="margin: 0 0 6px; font-size: 15px;">
                    <strong>{listing.job_title}</strong>
                    </p>

                    <p style="margin: 0; font-size: 13px; color: #555;">
                    🏢 <strong>{listing.firm}</strong>
                    &nbsp;•&nbsp;
                    📍 {listing.location}
                    </p>

                    <p style="margin: 4px 0 0; font-size: 12px; color: #666;">
                    Job ID: {listing.job_id}
                    </p>

                    <p style="margin: 4px 0 0; font-size: 12px;">
                    Status:
                    <strong style="color: {'#2e7d32' if listing.status == 'NEW' else '#c62828'};">
                    {listing.status}
                    </strong>
                    </p>

                    <p style="margin: 8px 0 0;">
                    <a href="{listing.url}" target="_blank" style="color: #1a73e8; text-decoration: none;">
                    View Job →
                    </a>
                    </p>
                    </div>
                """
            for listing in job_listings
        )
        return template.replace(
            '<!-- JOB_ITEMS_START -->\n    <!-- JOB_ITEMS_END -->',
            job_items_html
        )
