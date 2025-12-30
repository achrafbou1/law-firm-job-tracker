import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mail.provider import EmailProvider


@dataclass
class GmailService(EmailProvider):
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 587

    def send(
        self,
        to: str,
        subject: str,
        body: str
    ) -> None:
        msg = self._build_message(to, subject, body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())

    def _build_message(self, to, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        return msg
