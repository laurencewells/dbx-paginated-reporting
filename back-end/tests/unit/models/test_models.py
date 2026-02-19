"""
Unit tests for Pydantic domain models.

Tests validate field types, defaults, required fields, and model serialisation.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.structure import Structure, StructureCreate, StructureField, StructureTable, StructureUpdate
from models.template import Template, TemplateCreate, TemplateUpdate
from models.me import Me
from models.databasehealth import DatabaseHealth

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# StructureField
# ---------------------------------------------------------------------------


class TestStructureField:
    def test_valid_field_with_no_children(self):
        f = StructureField(name="revenue", type="number")
        assert f.name == "revenue"
        assert f.type == "number"
        assert f.children is None

    def test_valid_field_with_children(self):
        children = [StructureField(name="city", type="string")]
        f = StructureField(name="address", type="object", children=children)
        assert len(f.children) == 1

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            StructureField(type="string")  # type: ignore[call-arg]

    def test_type_is_required(self):
        with pytest.raises(ValidationError):
            StructureField(name="col")  # type: ignore[call-arg]

    def test_str_strip_whitespace(self):
        f = StructureField(name="  col  ", type="  string  ")
        assert f.name == "col"
        assert f.type == "string"


# ---------------------------------------------------------------------------
# StructureTable
# ---------------------------------------------------------------------------


class TestStructureTable:
    def test_valid_table(self):
        t = StructureTable(full_name="cat.sch.tbl", alias="tbl")
        assert t.full_name == "cat.sch.tbl"
        assert t.alias == "tbl"

    def test_full_name_is_required(self):
        with pytest.raises(ValidationError):
            StructureTable(alias="t")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


class TestStructure:
    def _make(self, **kwargs) -> Structure:
        defaults = dict(
            id=uuid.uuid4(),
            name="Test",
            project_id=uuid.uuid4(),
            fields=[],
            tables=[],
            relationships=[],
            selected_columns=[],
            sql_query=None,
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return Structure(**defaults)

    def test_minimal_valid_structure(self):
        s = self._make()
        assert isinstance(s.id, uuid.UUID)

    def test_fields_default_to_empty_list(self):
        s = self._make()
        assert s.fields == []

    def test_selected_columns_default_to_empty_list(self):
        s = self._make()
        assert s.selected_columns == []

    def test_sql_query_defaults_to_none(self):
        s = self._make()
        assert s.sql_query is None

    def test_id_is_required(self):
        with pytest.raises(ValidationError):
            Structure(name="T", created_at=NOW, updated_at=NOW)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# StructureCreate
# ---------------------------------------------------------------------------


class TestStructureCreate:
    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            StructureCreate()  # type: ignore[call-arg]

    def test_defaults_are_empty_lists(self):
        sc = StructureCreate(name="New", project_id=uuid.uuid4())
        assert sc.fields == []
        assert sc.tables == []
        assert sc.selected_columns == []


# ---------------------------------------------------------------------------
# StructureUpdate
# ---------------------------------------------------------------------------


class TestStructureUpdate:
    def test_all_fields_optional(self):
        su = StructureUpdate()
        assert su.name is None
        assert su.fields is None
        assert su.tables is None
        assert su.selected_columns is None


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------


class TestTemplate:
    def _make(self, **kwargs) -> Template:
        defaults = dict(
            id=uuid.uuid4(),
            name="Template",
            structure_id=uuid.uuid4(),
            html_content="<p>hello</p>",
            created_at=NOW,
            updated_at=NOW,
        )
        defaults.update(kwargs)
        return Template(**defaults)

    def test_valid_template(self):
        t = self._make()
        assert isinstance(t.id, uuid.UUID)

    def test_html_content_defaults_to_empty_string(self):
        t = Template(
            id=uuid.uuid4(),
            name="T",
            structure_id=uuid.uuid4(),
            created_at=NOW,
            updated_at=NOW,
        )
        assert t.html_content == ""

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            Template(id=uuid.uuid4(), structure_id=uuid.uuid4(), created_at=NOW, updated_at=NOW)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# TemplateCreate
# ---------------------------------------------------------------------------


class TestTemplateCreate:
    def test_valid_create(self):
        tc = TemplateCreate(name="New", structure_id=uuid.uuid4())
        assert tc.html_content == ""

    def test_structure_id_is_required(self):
        with pytest.raises(ValidationError):
            TemplateCreate(name="New")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# TemplateUpdate
# ---------------------------------------------------------------------------


class TestTemplateUpdate:
    def test_all_fields_optional(self):
        tu = TemplateUpdate()
        assert tu.name is None
        assert tu.structure_id is None
        assert tu.html_content is None


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------


class TestMe:
    def test_valid_me(self):
        me = Me(username="Alice", ip="127.0.0.1", email="alice@example.com")
        assert me.username == "Alice"

    def test_invalid_email_raises_validation_error(self):
        with pytest.raises(ValidationError):
            Me(username="Alice", ip="127.0.0.1", email="not-an-email")

    def test_username_is_required(self):
        with pytest.raises(ValidationError):
            Me(ip="127.0.0.1", email="a@b.com")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# DatabaseHealth
# ---------------------------------------------------------------------------


class TestDatabaseHealth:
    def test_healthy_status(self):
        dh = DatabaseHealth(
            lakebase_configured=True,
            database_instance_exists=True,
            connection_healthy=True,
            status="healthy",
            connection_info=None,
            error=None,
        )
        assert dh.status == "healthy"

    def test_unhealthy_status(self):
        dh = DatabaseHealth(
            lakebase_configured=False,
            database_instance_exists=False,
            connection_healthy=False,
            status="unhealthy",
            connection_info=None,
            error="Something failed",
        )
        assert dh.error == "Something failed"

    def test_invalid_status_raises_validation_error(self):
        with pytest.raises(ValidationError):
            DatabaseHealth(
                lakebase_configured=False,
                database_instance_exists=False,
                connection_healthy=False,
                status="degraded",  # not in Literal["healthy", "unhealthy"]
                connection_info=None,
                error=None,
            )
