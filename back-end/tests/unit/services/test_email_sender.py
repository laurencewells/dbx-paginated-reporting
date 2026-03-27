"""
Unit tests for common.email.sender.

All external calls (Databricks secrets, smtplib) are mocked.
"""
from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.email.sender import _get_secret, send_report_email, send_report_email_with_attachment


# ---------------------------------------------------------------------------
# _get_secret
# ---------------------------------------------------------------------------


class TestGetSecret:
    def test_returns_decoded_secret_value(self):
        import base64
        mock_client = MagicMock()
        mock_client.secrets.get_secret.return_value = MagicMock(
            value=base64.b64encode(b"my-password").decode()
        )

        with patch("common.authentication.workspace.WorkspaceAuthentication") as MockAuth:
            MockAuth.return_value.client = mock_client
            result = _get_secret("my-scope", "my-key")

        assert result == "my-password"
        mock_client.secrets.get_secret.assert_called_once_with(scope="my-scope", key="my-key")


# ---------------------------------------------------------------------------
# send_report_email
# ---------------------------------------------------------------------------


class TestSendReportEmail:
    @pytest.mark.asyncio
    async def test_sends_email_successfully(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with (
            patch("common.email.sender._get_secret", return_value="secret-pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="user@example.com",
                secret_scope="my-scope",
                secret_key="my-key",
                from_email="from@example.com",
                recipients=["alice@example.com", "bob@example.com"],
                subject="Test Report",
                html_body="<h1>Hello</h1>",
            )

        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@example.com", "secret-pw")
        mock_smtp.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_sendmail_called_with_correct_from_and_recipients(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with (
            patch("common.email.sender._get_secret", return_value="pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="user@example.com",
                secret_scope="scope",
                secret_key="key",
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Subject",
                html_body="<p>body</p>",
            )

        call_args = mock_smtp.sendmail.call_args[0]
        assert call_args[0] == "from@example.com"
        assert call_args[1] == ["alice@example.com"]

    @pytest.mark.asyncio
    async def test_smtp_constructed_with_correct_host_and_port(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with (
            patch("common.email.sender._get_secret", return_value="pw"),
            patch("smtplib.SMTP", return_value=mock_smtp) as MockSMTP,
        ):
            await send_report_email(
                smtp_host="smtp.custom.com",
                smtp_port=465,
                username="u",
                secret_scope="s",
                secret_key="k",
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                html_body="body",
            )

        MockSMTP.assert_called_once_with("smtp.custom.com", 465, timeout=30)

    @pytest.mark.asyncio
    async def test_to_header_joins_recipients(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        captured_msg = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured_msg["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail

        with (
            patch("common.email.sender._get_secret", return_value="pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="u",
                secret_scope="s",
                secret_key="k",
                from_email="f@example.com",
                recipients=["alice@example.com", "bob@example.com"],
                subject="Multi",
                html_body="<p>body</p>",
            )

        assert "alice@example.com" in captured_msg["raw"]
        assert "bob@example.com" in captured_msg["raw"]

    @pytest.mark.asyncio
    async def test_propagates_smtp_errors(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b"auth failed")

        with (
            patch("common.email.sender._get_secret", return_value="wrong"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            with pytest.raises(smtplib.SMTPAuthenticationError):
                await send_report_email(
                    smtp_host="smtp.example.com",
                    smtp_port=587,
                    username="u",
                    secret_scope="s",
                    secret_key="k",
                    from_email="f@example.com",
                    recipients=["r@example.com"],
                    subject="S",
                    html_body="body",
                )


# ---------------------------------------------------------------------------
# send_report_email_with_attachment
# ---------------------------------------------------------------------------


class TestSendReportEmailWithAttachment:
    @pytest.mark.asyncio
    async def test_sends_pdf_attachment_successfully(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with (
            patch("common.email.sender._get_secret", return_value="secret-pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email_with_attachment(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="user@example.com",
                secret_scope="my-scope",
                secret_key="my-key",
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Monthly Report",
                pdf_bytes=b"%PDF-1.4 fake",
                filename="report.pdf",
            )

        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("user@example.com", "secret-pw")
        mock_smtp.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_attachment_filename_in_message(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        captured: dict = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail

        with (
            patch("common.email.sender._get_secret", return_value="pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email_with_attachment(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="u",
                secret_scope="s",
                secret_key="k",
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                pdf_bytes=b"%PDF",
                filename="my_report.pdf",
            )

        assert "my_report.pdf" in captured["raw"]

    @pytest.mark.asyncio
    async def test_sendmail_called_with_correct_recipients(self):
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with (
            patch("common.email.sender._get_secret", return_value="pw"),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            await send_report_email_with_attachment(
                smtp_host="smtp.example.com",
                smtp_port=587,
                username="u",
                secret_scope="s",
                secret_key="k",
                from_email="f@example.com",
                recipients=["alice@example.com", "bob@example.com"],
                subject="S",
                pdf_bytes=b"%PDF",
                filename="r.pdf",
            )

        call_args = mock_smtp.sendmail.call_args[0]
        assert call_args[0] == "f@example.com"
        assert call_args[1] == ["alice@example.com", "bob@example.com"]


# ---------------------------------------------------------------------------
# SendGrid API path
# ---------------------------------------------------------------------------


class TestSendGridProvider:
    def _mock_sg_response(self, status_code: int = 202):
        resp = MagicMock()
        resp.status_code = status_code
        resp.body = b""
        return resp

    @pytest.mark.asyncio
    async def test_send_html_uses_sendgrid_client(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = self._mock_sg_response()

        with (
            patch("common.email.sender._get_secret", return_value="SG.test-api-key"),
            patch("sendgrid.SendGridAPIClient", return_value=mock_sg),
        ):
            await send_report_email(
                provider="sendgrid",
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Test",
                html_body="<h1>Hi</h1>",
                secret_scope="scope",
                secret_key="key",
            )

        mock_sg.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_html_sendgrid_raises_on_4xx(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = self._mock_sg_response(status_code=400)

        with (
            patch("common.email.sender._get_secret", return_value="SG.bad-key"),
            patch("sendgrid.SendGridAPIClient", return_value=mock_sg),
        ):
            with pytest.raises(RuntimeError, match="SendGrid API error 400"):
                await send_report_email(
                    provider="sendgrid",
                    from_email="from@example.com",
                    recipients=["r@example.com"],
                    subject="S",
                    html_body="body",
                    secret_scope="s",
                    secret_key="k",
                )

    @pytest.mark.asyncio
    async def test_send_attachment_sendgrid_calls_sdk(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = self._mock_sg_response()

        with (
            patch("common.email.sender._get_secret", return_value="SG.test-api-key"),
            patch("sendgrid.SendGridAPIClient", return_value=mock_sg),
        ):
            await send_report_email_with_attachment(
                provider="sendgrid",
                from_email="from@example.com",
                recipients=["r@example.com"],
                subject="Report",
                pdf_bytes=b"%PDF",
                filename="report.pdf",
                secret_scope="s",
                secret_key="k",
            )

        mock_sg.send.assert_called_once()
