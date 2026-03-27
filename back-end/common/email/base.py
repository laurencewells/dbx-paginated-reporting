"""Abstract base class for email providers."""
from abc import ABC, abstractmethod
from typing import List


class EmailProvider(ABC):
    """Each concrete provider handles its own credential and transport details."""

    @abstractmethod
    async def send_html(
        self,
        from_email: str,
        recipients: List[str],
        subject: str,
        html_body: str,
    ) -> None:
        """Send the rendered report as an inline HTML email body."""

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
