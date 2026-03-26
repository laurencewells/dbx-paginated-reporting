"""
Unit tests for SmtpConnection and EmailSendList Pydantic models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.email_send_list import EmailSendList, EmailSendListCreate, EmailSendListUpdate
from models.smtp_connection import SmtpConnection, SmtpConnectionCreate, SmtpConnectionUpdate

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
CID = uuid.uuid4()
PID = uuid.uuid4()
SLID = uuid.uuid4()


# ---------------------------------------------------------------------------
# SmtpConnection
# ---------------------------------------------------------------------------


class TestSmtpConnection:
    def _make(self, **kwargs) -> SmtpConnection:
        defaults = dict(
            id=CID,
            name="My SMTP",
            provider="gsuite",
            from_email="sender@example.com",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="sender@example.com",
            secret_scope="paginated-reports-smtp",
            secret_key=f"smtp_{CID}",
            created_by="admin@example.com",
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return SmtpConnection(**defaults)

    def test_basic_construction(self):
        conn = self._make()
        assert conn.name == "My SMTP"
        assert conn.provider == "gsuite"
        assert conn.smtp_port == 587

    def test_id_is_uuid(self):
        conn = self._make()
        assert isinstance(conn.id, uuid.UUID)

    def test_roundtrip_json(self):
        conn = self._make()
        data = conn.model_dump()
        restored = SmtpConnection(**data)
        assert restored.id == conn.id
        assert restored.smtp_host == conn.smtp_host


class TestSmtpConnectionCreate:
    def _make(self, **kwargs) -> SmtpConnectionCreate:
        defaults = dict(
            name="My SMTP",
            provider="gsuite",
            from_email="sender@example.com",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="sender@example.com",
            password="secret123",
        )
        defaults.update(kwargs)
        return SmtpConnectionCreate(**defaults)

    def test_valid_create(self):
        c = self._make()
        assert c.name == "My SMTP"
        assert c.smtp_port == 587

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            self._make(from_email="not-an-email")

    def test_whitespace_stripped(self):
        c = self._make(name="  trimmed  ")
        assert c.name == "trimmed"

    def test_default_smtp_port(self):
        c = SmtpConnectionCreate(
            name="X",
            provider="gsuite",
            from_email="a@b.com",
            smtp_host="smtp.example.com",
            username="u",
            password="p",
        )
        assert c.smtp_port == 587


class TestSmtpConnectionUpdate:
    def test_all_none_is_valid(self):
        u = SmtpConnectionUpdate()
        assert u.name is None
        assert u.password is None

    def test_partial_update(self):
        u = SmtpConnectionUpdate(name="New Name")
        assert u.name == "New Name"
        assert u.smtp_host is None

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            SmtpConnectionUpdate(from_email="bad-email")

    def test_valid_email_accepted(self):
        u = SmtpConnectionUpdate(from_email="good@example.com")
        assert str(u.from_email) == "good@example.com"


# ---------------------------------------------------------------------------
# EmailSendList
# ---------------------------------------------------------------------------


class TestEmailSendList:
    def _make(self, **kwargs) -> EmailSendList:
        defaults = dict(
            id=SLID,
            name="Exec List",
            project_id=PID,
            smtp_connection_id=CID,
            emails=["alice@example.com", "bob@example.com"],
            created_by="admin@example.com",
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return EmailSendList(**defaults)

    def test_basic_construction(self):
        sl = self._make()
        assert sl.name == "Exec List"
        assert len(sl.emails) == 2

    def test_empty_emails_allowed(self):
        sl = self._make(emails=[])
        assert sl.emails == []

    def test_roundtrip_json(self):
        sl = self._make()
        data = sl.model_dump()
        restored = EmailSendList(**data)
        assert restored.emails == sl.emails


class TestEmailSendListCreate:
    def _make(self, **kwargs) -> EmailSendListCreate:
        defaults = dict(
            name="Exec List",
            project_id=PID,
            smtp_connection_id=CID,
            emails=["alice@example.com"],
        )
        defaults.update(kwargs)
        return EmailSendListCreate(**defaults)

    def test_valid_create(self):
        c = self._make()
        assert c.name == "Exec List"
        assert len(c.emails) == 1

    def test_invalid_email_in_list_rejected(self):
        with pytest.raises(ValidationError):
            self._make(emails=["not-an-email"])

    def test_empty_emails_default(self):
        c = EmailSendListCreate(
            name="X",
            project_id=PID,
            smtp_connection_id=CID,
        )
        assert c.emails == []

    def test_whitespace_stripped_from_name(self):
        c = self._make(name="  padded  ")
        assert c.name == "padded"


class TestEmailSendListUpdate:
    def test_all_none_is_valid(self):
        u = EmailSendListUpdate()
        assert u.name is None
        assert u.emails is None

    def test_partial_update(self):
        u = EmailSendListUpdate(name="New Name")
        assert u.name == "New Name"

    def test_invalid_email_in_list_rejected(self):
        with pytest.raises(ValidationError):
            EmailSendListUpdate(emails=["bad-email"])

    def test_valid_partial_emails_update(self):
        u = EmailSendListUpdate(emails=["new@example.com"])
        assert len(u.emails) == 1
