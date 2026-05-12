"""SMTP email provider using smtplib STARTTLS.

Handles both 'gsuite' and 'smtp' provider types — they are mechanically
identical; the distinction is only that gsuite auto-fills host/port defaults
in the UI.
"""
import asyncio
import os
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Tuple

from common.email.base import CID_DOMAIN, EmailProvider
from common.logger import log as L

try:
    _SMTP_TIMEOUT_SECONDS = int(os.getenv("SMTP_TIMEOUT_SECONDS", "30"))
except ValueError:
    L.warning("Invalid SMTP_TIMEOUT_SECONDS value in environment; using default of 30 seconds.")
    _SMTP_TIMEOUT_SECONDS = 30


class SmtpEmailProvider(EmailProvider):
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def _build_connection(self) -> smtplib.SMTP:
        server = smtplib.SMTP(self._host, self._port, timeout=_SMTP_TIMEOUT_SECONDS)
        server.ehlo()
        server.starttls()
        server.login(self._username, self._password)
        return server

    def _send_html_blocking(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        cid_images: Optional[Dict[str, Tuple[str, bytes]]] = None,
    ) -> None:
        if cid_images:
            # multipart/related wraps the HTML alternative + inline image parts
            msg = MIMEMultipart("related")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = ", ".join(recipients)
            alt = MIMEMultipart("alternative")
            alt.attach(MIMEText(html_body, "html"))
            msg.attach(alt)
            for uid, (mime_type, image_bytes) in cid_images.items():
                maintype, subtype = mime_type.split("/", 1)
                img_part = MIMEBase(maintype, subtype)
                img_part.set_payload(image_bytes)
                encoders.encode_base64(img_part)
                img_part.add_header("Content-ID", f"<{uid}@{CID_DOMAIN}>")
                img_part.add_header("Content-Disposition", "inline")
                msg.attach(img_part)
        else:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(html_body, "html"))
        with self._build_connection() as server:
            server.sendmail(from_email, recipients, msg.as_string())

    def _send_attachment_blocking(
        self, from_email: str, recipients: List[str], subject: str,
        pdf_bytes: bytes, filename: str,
    ) -> None:
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText("Please find the report attached.", "plain"))
        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)
        with self._build_connection() as server:
            server.sendmail(from_email, recipients, msg.as_string())

    async def send_html(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        cid_images: Optional[Dict[str, Tuple[str, bytes]]] = None,
    ) -> None:
        await asyncio.to_thread(self._send_html_blocking, from_email, recipients, subject, html_body, cid_images)
        L.info(f"[Email] Sent HTML body to {len(recipients)} recipient(s) via {self._host}")

    async def send_attachment(
        self, from_email: str, recipients: List[str], subject: str,
        pdf_bytes: bytes, filename: str,
    ) -> None:
        await asyncio.to_thread(self._send_attachment_blocking, from_email, recipients, subject, pdf_bytes, filename)
        L.info(f"[Email] Sent PDF attachment ({filename}) to {len(recipients)} recipient(s) via {self._host}")
