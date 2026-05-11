"""SendGrid email provider using the sendgrid-python SDK."""
import asyncio
import base64 as _base64
from typing import Dict, List, Optional, Tuple

from common.email.base import EmailProvider
from common.logger import log as L


class SendGridEmailProvider(EmailProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _send_html_blocking(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        cid_images: Optional[Dict[str, Tuple[str, bytes]]] = None,
    ) -> None:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import (
            Attachment, ContentId, Disposition, FileContent, FileName, FileType, Mail,
        )

        message = Mail(
            from_email=from_email,
            to_emails=recipients,
            subject=subject,
            html_content=html_body,
        )
        if cid_images:
            for uid, (mime_type, image_bytes) in cid_images.items():
                message.attachment = Attachment(
                    FileContent(_base64.b64encode(image_bytes).decode()),
                    FileName(uid),
                    FileType(mime_type),
                    Disposition("inline"),
                    ContentId(f"{uid}@report"),
                )
        response = SendGridAPIClient(self._api_key).send(message)
        if response.status_code >= 400:
            raise RuntimeError(f"SendGrid API error {response.status_code}: {response.body}")

    def _send_attachment_blocking(
        self, from_email: str, recipients: List[str], subject: str,
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
        response = SendGridAPIClient(self._api_key).send(message)
        if response.status_code >= 400:
            raise RuntimeError(f"SendGrid API error {response.status_code}: {response.body}")

    async def send_html(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        cid_images: Optional[Dict[str, Tuple[str, bytes]]] = None,
    ) -> None:
        await asyncio.to_thread(self._send_html_blocking, from_email, recipients, subject, html_body, cid_images)
        L.info(f"[Email] Sent HTML body to {len(recipients)} recipient(s) via SendGrid API")

    async def send_attachment(
        self, from_email: str, recipients: List[str], subject: str,
        pdf_bytes: bytes, filename: str,
    ) -> None:
        await asyncio.to_thread(self._send_attachment_blocking, from_email, recipients, subject, pdf_bytes, filename)
        L.info(f"[Email] Sent PDF attachment ({filename}) to {len(recipients)} recipient(s) via SendGrid API")
