from datetime import datetime
from pathlib import Path

from loguru import logger
from python_http_client.exceptions import ForbiddenError, UnauthorizedError
from sendgrid import Mail, SendGridAPIClient
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.constants import TIMEZONE
from src.services.airtable.models.job_listing import JobListing
from src.services.email.provider import EmailProvider
from src.settings import settings

# Path to email templates directory
TEMPLATES_DIR = Path(__file__).parent / 'templates'


class SendGridEmailService(EmailProvider):
    _client: SendGridAPIClient

    def __init__(self):
        self._client = SendGridAPIClient(api_key=settings.sendgrid_api_key)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    def send_jobs_email(self, body: str, ats: str) -> None:
        now = datetime.now(TIMEZONE)
        subject = f'📢 New Jobs {now.month}/{now.day}/{now.strftime("%y")} for ATS {ats}'

        email = Mail(
            from_email=settings.sender_email,
            to_emails=settings.receiver_email,
            subject=subject,
            html_content=body
        )
        if settings.debug_email:
            email.add_cc(settings.debug_email)

        try:
            self._client.send(email)
        except (ForbiddenError, UnauthorizedError) as exc:
            logger.error(
                'SendGrid authentication failed ({}). '
                'Verify your SENDGRID_API_KEY and that the sender email '
                '"{}" is verified in SendGrid.',
                type(exc).__name__,
                settings.sender_email,
            )
            raise

    def get_job_listings_summary(self, job_listings: list[JobListing]) -> str:
        template = (TEMPLATES_DIR / 'job_updates_email.html').read_text(encoding='utf-8')
        job_items_html = ''.join(
            f"""
                <div style="margin-bottom: 16px; padding: 12px;
                     border: 1px solid #ddd; border-radius: 6px;">
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
                    <a href="{listing.url}" target="_blank"
                       style="color: #1a73e8; text-decoration: none;">
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
