"""
Unit tests for the email provider classes.

All external calls (Databricks secrets, smtplib, SendGrid SDK) are mocked.
"""
from __future__ import annotations

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from common.email._secret import get_secret
from common.email.base import CID_DOMAIN
from common.email.providers.sendgrid import SendGridEmailProvider
from common.email.providers.smtp import SmtpEmailProvider


# ---------------------------------------------------------------------------
# get_secret
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
            result = get_secret("my-scope", "my-key")

        assert result == "my-password"
        mock_client.secrets.get_secret.assert_called_once_with(scope="my-scope", key="my-key")


# ---------------------------------------------------------------------------
# SmtpEmailProvider
# ---------------------------------------------------------------------------


def _mock_smtp_server():
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


class TestSmtpEmailProviderSendHtml:
    @pytest.mark.asyncio
    async def test_sends_email_successfully(self):
        mock_smtp = _mock_smtp_server()
        provider = SmtpEmailProvider("smtp.example.com", 587, "user@example.com", "secret-pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_html(
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
        mock_smtp = _mock_smtp_server()
        provider = SmtpEmailProvider("smtp.example.com", 587, "user@example.com", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_html(
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
        mock_smtp = _mock_smtp_server()
        provider = SmtpEmailProvider("smtp.custom.com", 465, "u", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp) as MockSMTP:
            await provider.send_html(
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                html_body="body",
            )

        MockSMTP.assert_called_once_with("smtp.custom.com", 465, timeout=30)

    @pytest.mark.asyncio
    async def test_to_header_joins_recipients(self):
        mock_smtp = _mock_smtp_server()
        captured: dict = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_html(
                from_email="f@example.com",
                recipients=["alice@example.com", "bob@example.com"],
                subject="Multi",
                html_body="<p>body</p>",
            )

        assert "alice@example.com" in captured["raw"]
        assert "bob@example.com" in captured["raw"]

    @pytest.mark.asyncio
    async def test_propagates_smtp_errors(self):
        mock_smtp = _mock_smtp_server()
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b"auth failed")
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "wrong")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            with pytest.raises(smtplib.SMTPAuthenticationError):
                await provider.send_html(
                    from_email="f@example.com",
                    recipients=["r@example.com"],
                    subject="S",
                    html_body="body",
                )

    @pytest.mark.asyncio
    async def test_cid_images_produce_multipart_related(self):
        mock_smtp = _mock_smtp_server()
        captured: dict = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "pw")
        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        cid_images = {uid: ("image/png", b"\x89PNG\r\n")}

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_html(
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                html_body=f'<img src="cid:{uid}@{CID_DOMAIN}" />',
                cid_images=cid_images,
            )

        assert "multipart/related" in captured["raw"]
        assert f"{uid}@{CID_DOMAIN}" in captured["raw"]

    @pytest.mark.asyncio
    async def test_no_cid_images_produces_multipart_alternative(self):
        mock_smtp = _mock_smtp_server()
        captured: dict = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_html(
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                html_body="<p>no images</p>",
            )

        assert "multipart/alternative" in captured["raw"]
        assert "multipart/related" not in captured["raw"]


class TestSmtpEmailProviderSendAttachment:
    @pytest.mark.asyncio
    async def test_sends_pdf_attachment_successfully(self):
        mock_smtp = _mock_smtp_server()
        provider = SmtpEmailProvider("smtp.example.com", 587, "user@example.com", "secret-pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_attachment(
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
        mock_smtp = _mock_smtp_server()
        captured: dict = {}

        def capture_sendmail(from_addr, to_addrs, msg_str):
            captured["raw"] = msg_str

        mock_smtp.sendmail.side_effect = capture_sendmail
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_attachment(
                from_email="f@example.com",
                recipients=["r@example.com"],
                subject="S",
                pdf_bytes=b"%PDF",
                filename="my_report.pdf",
            )

        assert "my_report.pdf" in captured["raw"]

    @pytest.mark.asyncio
    async def test_sendmail_called_with_correct_recipients(self):
        mock_smtp = _mock_smtp_server()
        provider = SmtpEmailProvider("smtp.example.com", 587, "u", "pw")

        with patch("smtplib.SMTP", return_value=mock_smtp):
            await provider.send_attachment(
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
# SendGridEmailProvider
# ---------------------------------------------------------------------------


def _mock_sg_response(status_code: int = 202):
    resp = MagicMock()
    resp.status_code = status_code
    resp.body = b""
    return resp


class TestSendGridEmailProvider:
    @pytest.mark.asyncio
    async def test_send_html_uses_sendgrid_client(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = _mock_sg_response()
        provider = SendGridEmailProvider(api_key="SG.test-api-key")

        with patch("sendgrid.SendGridAPIClient", return_value=mock_sg):
            await provider.send_html(
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Test",
                html_body="<h1>Hi</h1>",
            )

        mock_sg.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_html_raises_on_4xx(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = _mock_sg_response(status_code=400)
        provider = SendGridEmailProvider(api_key="SG.bad-key")

        with patch("sendgrid.SendGridAPIClient", return_value=mock_sg):
            with pytest.raises(RuntimeError, match="SendGrid API error 400"):
                await provider.send_html(
                    from_email="from@example.com",
                    recipients=["r@example.com"],
                    subject="S",
                    html_body="body",
                )

    @pytest.mark.asyncio
    async def test_send_attachment_calls_sdk(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = _mock_sg_response()
        provider = SendGridEmailProvider(api_key="SG.test-api-key")

        with patch("sendgrid.SendGridAPIClient", return_value=mock_sg):
            await provider.send_attachment(
                from_email="from@example.com",
                recipients=["r@example.com"],
                subject="Report",
                pdf_bytes=b"%PDF",
                filename="report.pdf",
            )

        mock_sg.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_cid_images_added_as_inline_attachments(self):
        mock_sg = MagicMock()
        mock_sg.send.return_value = _mock_sg_response()
        provider = SendGridEmailProvider(api_key="SG.test-api-key")
        uid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        cid_images = {uid: ("image/png", b"\x89PNG\r\n")}

        with patch("sendgrid.SendGridAPIClient", return_value=mock_sg):
            await provider.send_html(
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Test",
                html_body=f'<img src="cid:{uid}@{CID_DOMAIN}" />',
                cid_images=cid_images,
            )

        mock_sg.send.assert_called_once()
        mail_obj = mock_sg.send.call_args[0][0]
        # mail.attachment is write-only; serialised state is the source of truth
        attachments = mail_obj.get().get("attachments", [])
        assert len(attachments) == 1
        assert attachments[0]["disposition"] == "inline"
        assert attachments[0]["content_id"] == f"{uid}@{CID_DOMAIN}"

    @pytest.mark.asyncio
    async def test_cid_images_multiple_all_attached(self):
        """Regression: assigning message.attachment in a loop dropped all but one."""
        mock_sg = MagicMock()
        mock_sg.send.return_value = _mock_sg_response()
        provider = SendGridEmailProvider(api_key="SG.test-api-key")
        uid_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        uid_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        cid_images = {
            uid_a: ("image/png", b"\x89PNG-a"),
            uid_b: ("image/jpeg", b"\xff\xd8\xff-b"),
        }

        with patch("sendgrid.SendGridAPIClient", return_value=mock_sg):
            await provider.send_html(
                from_email="from@example.com",
                recipients=["alice@example.com"],
                subject="Test",
                html_body=f'<img src="cid:{uid_a}@{CID_DOMAIN}" /><img src="cid:{uid_b}@{CID_DOMAIN}" />',
                cid_images=cid_images,
            )

        mail_obj = mock_sg.send.call_args[0][0]
        attachments = mail_obj.get().get("attachments", [])
        assert len(attachments) == 2
        content_ids = {a["content_id"] for a in attachments}
        assert content_ids == {f"{uid_a}@{CID_DOMAIN}", f"{uid_b}@{CID_DOMAIN}"}
        assert all(a["disposition"] == "inline" for a in attachments)
