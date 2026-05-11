"""Abstract base class for email providers."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class EmailProvider(ABC):
    """Each concrete provider handles its own credential and transport details."""

    @abstractmethod
    async def send_html(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        cid_images: Optional[Dict[str, Tuple[str, bytes]]] = None,
    ) -> None:
        """Send the rendered report as an inline HTML email body.

        cid_images: optional mapping of {uuid: (mime_type, raw_bytes)} for images
        that have already been rewritten to src="cid:uuid@report" in html_body.
        Each entry is embedded as a MIME inline attachment so email clients
        (including Gmail and Outlook) render them without stripping.
        """

    @abstractmethod
    async def send_attachment(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        pdf_bytes: bytes,
        filename: str,
    ) -> None:
        """Send the rendered report as a PDF attachment."""
