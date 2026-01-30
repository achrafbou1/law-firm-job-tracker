import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

from airtable.models.job_listing import JobListing
from mail.provider import EmailProvider


@dataclass
class GmailService(EmailProvider):
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 465

    def send_jobs_email(
            self,
            to: list[str],
            body: str
    ) -> None:

        now = datetime.now(ZoneInfo('America/New_York'))
        subject = f'📢 New Jobs {now.month}/{now.day}/{now.strftime('%y')}'
        msg = self._build_message(to, subject, body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            logging.info(f"Sent email to {to} with subject '{subject}' successfully")
            server.quit()

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
