"""
Email delivery utility supporting SMTP (smtplib) and SendGrid API.

Retrieves credentials from the Databricks Secret Store and sends
the rendered report either as an HTML email body (for 'email' page_size
templates) or as an attached PDF (for print-layout templates like 'A4').

Provider routing:
  - provider == "sendgrid"  → SendGrid Python SDK (API key-based)
  - all others              → smtplib STARTTLS
"""
import asyncio
import base64 as _base64
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from common.logger import log as L

_SMTP_TIMEOUT_SECONDS = 30


async def _run_blocking(func, *args):
    # Run blocking call in a thread without using deprecated get_event_loop()
    return await asyncio.to_thread(func, *args)


def _get_secret(scope: str, key: str) -> str:
    from common.authentication.workspace import WorkspaceAuthentication
    client = WorkspaceAuthentication().client
    encoded = client.secrets.get_secret(scope=scope, key=key).value
    return _base64.b64decode(encoded).decode("utf-8")


# -- SMTP (smtplib) -----------------------------------------------------------

def _send_html_blocking(
    smtp_host: str, smtp_port: int, username: str, password: str,
    from_email: str, recipients: List[str], subject: str, html_body: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(smtp_host, smtp_port, timeout=_SMTP_TIMEOUT_SECONDS) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, recipients, msg.as_string())


def _send_attachment_blocking(
    smtp_host: str, smtp_port: int, username: str, password: str,
    from_email: str, recipients: List[str], subject: str, pdf_bytes: bytes, filename: str,
) -> None:
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText("Please find the report attached.", "plain"))
    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)
    with smtplib.SMTP(smtp_host, smtp_port, timeout=_SMTP_TIMEOUT_SECONDS) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, recipients, msg.as_string())


# -- SendGrid API (sendgrid-python SDK) ---------------------------------------

def _send_html_sendgrid_blocking(
    api_key: str, from_email: str, recipients: List[str], subject: str, html_body: str,
) -> None:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=from_email,
        to_emails=recipients,
        subject=subject,
        html_content=html_body,
    )
    response = SendGridAPIClient(api_key).send(message)
    if response.status_code >= 400:
        raise RuntimeError(f"SendGrid API error {response.status_code}: {response.body}")


def _send_attachment_sendgrid_blocking(
    api_key: str, from_email: str, recipients: List[str], subject: str,
    pdf_bytes: bytes, filename: str,
) -> None:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (
        Attachment, Disposition, FileContent, FileName, FileType, Mail,
    )

    message = Mail(
        from_email=from_email,
        to_emails=recipients,
        subject=subject,
        plain_text_content="Please find the report attached.",
    )
    message.attachment = Attachment(
        FileContent(_base64.b64encode(pdf_bytes).decode()),
        FileName(filename),
        FileType("application/pdf"),
        Disposition("attachment"),
    )
    response = SendGridAPIClient(api_key).send(message)
    if response.status_code >= 400:
        raise RuntimeError(f"SendGrid API error {response.status_code}: {response.body}")


# -- Public async interface ---------------------------------------------------

async def send_report_email(
    from_email: str,
    recipients: List[str],
    subject: str,
    html_body: str,
    secret_scope: str,
    secret_key: str,
    provider: str = "",
    smtp_host: str = "",
    smtp_port: int = 587,
    username: str = "",
) -> None:
    """Send the rendered report as an inline HTML email body."""
    credential = _get_secret(secret_scope, secret_key)
    if provider == "sendgrid":
        await _run_blocking(_send_html_sendgrid_blocking, credential, from_email, recipients, subject, html_body)
        L.info(f"[Email] Sent HTML body to {len(recipients)} recipient(s) via SendGrid API")
    else:
        await _run_blocking(_send_html_blocking, smtp_host, smtp_port, username, credential, from_email, recipients, subject, html_body)
        L.info(f"[Email] Sent HTML body to {len(recipients)} recipient(s) via {smtp_host}")


async def send_report_email_with_attachment(
    from_email: str,
    recipients: List[str],
    subject: str,
    pdf_bytes: bytes,
    filename: str,
    secret_scope: str,
    secret_key: str,
    provider: str = "",
    smtp_host: str = "",
    smtp_port: int = 587,
    username: str = "",
) -> None:
    """Send the rendered report as a PDF attachment."""
    credential = _get_secret(secret_scope, secret_key)
    if provider == "sendgrid":
        await _run_blocking(_send_attachment_sendgrid_blocking, credential, from_email, recipients, subject, pdf_bytes, filename)
        L.info(f"[Email] Sent PDF attachment ({filename}) to {len(recipients)} recipient(s) via SendGrid API")
    else:
        await _run_blocking(_send_attachment_blocking, smtp_host, smtp_port, username, credential, from_email, recipients, subject, pdf_bytes, filename)
        L.info(f"[Email] Sent PDF attachment ({filename}) to {len(recipients)} recipient(s) via {smtp_host}")
