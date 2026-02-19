"""
Unit tests for prompt_builder.build_report_agent_prompt.

This is pure logic — no I/O, no mocking required.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest

from models.structure import Structure, StructureField, StructureTable
from models.template import Template
from services.prompt_builder import build_report_agent_prompt

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SENTINEL = object()


def _structure(
    *,
    name: str = "Sales Report",
    fields=_SENTINEL,
    tables=_SENTINEL,
    selected_columns=_SENTINEL,
    sql_query: str | None = None,
) -> Structure:
    return Structure(
        id=uuid.uuid4(),
        name=name,
        project_id=uuid.uuid4(),
        fields=[StructureField(name="revenue", type="number")] if fields is _SENTINEL else fields,
        tables=[StructureTable(full_name="cat.sch.sales", alias="sales")] if tables is _SENTINEL else tables,
        selected_columns=["revenue"] if selected_columns is _SENTINEL else selected_columns,
        sql_query=sql_query,
        created_at=NOW,
        updated_at=NOW,
    )


def _template(
    *,
    name: str = "Monthly Report",
    structure_id: uuid.UUID | None = None,
    html_content: str = "<p>{{#rows}}{{revenue}}{{/rows}}</p>",
) -> Template:
    return Template(
        id=uuid.uuid4(),
        name=name,
        structure_id=structure_id or uuid.uuid4(),
        html_content=html_content,
        created_at=NOW,
        updated_at=NOW,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBuildReportAgentPrompt:
    def test_returns_non_empty_string(self):
        prompt = build_report_agent_prompt(_structure(), _template())
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_includes_structure_name(self):
        prompt = build_report_agent_prompt(_structure(name="Revenue Dashboard"), _template())
        assert "Revenue Dashboard" in prompt

    def test_includes_template_name(self):
        prompt = build_report_agent_prompt(_structure(), _template(name="Q1 Summary"))
        assert "Q1 Summary" in prompt

    def test_includes_fields_as_json(self):
        fields = [
            StructureField(name="revenue", type="number"),
            StructureField(name="region", type="string"),
        ]
        prompt = build_report_agent_prompt(_structure(fields=fields), _template())
        assert "revenue" in prompt
        assert "region" in prompt

    def test_includes_sql_section_when_sql_query_and_tables_present(self):
        structure = _structure(
            sql_query="SELECT revenue FROM cat.sch.sales",
            tables=[StructureTable(full_name="cat.sch.sales", alias="sales")],
        )
        prompt = build_report_agent_prompt(structure, _template())
        assert "SELECT revenue FROM cat.sch.sales" in prompt
        assert "cat.sch.sales" in prompt
        # The conditional section header only appears when sql_query + tables are present
        assert "## Data Source" in prompt

    def test_omits_sql_section_when_no_sql_query(self):
        structure = _structure(sql_query=None)
        prompt = build_report_agent_prompt(structure, _template())
        # The ## Data Source header is only injected when sql_query is set
        assert "## Data Source" not in prompt

    def test_omits_sql_section_when_no_tables(self):
        structure = _structure(sql_query="SELECT 1", tables=[])
        prompt = build_report_agent_prompt(structure, _template())
        # With empty tables list, the sql_section block is not injected
        assert "## Data Source" not in prompt

    def test_includes_html_content_from_template(self):
        html = "<div>{{#rows}}<p>{{name}}</p>{{/rows}}</div>"
        prompt = build_report_agent_prompt(_structure(), _template(html_content=html))
        assert html in prompt

    def test_includes_selected_columns_when_sql_present(self):
        structure = _structure(
            sql_query="SELECT revenue, region FROM cat.sch.sales",
            selected_columns=["revenue", "region"],
            tables=[StructureTable(full_name="cat.sch.sales", alias="s")],
        )
        prompt = build_report_agent_prompt(structure, _template())
        assert "revenue" in prompt
        assert "region" in prompt

    def test_fields_json_is_valid_json(self):
        """The fields block embedded in the prompt must be parseable JSON."""
        fields = [
            StructureField(name="id", type="number"),
            StructureField(name="label", type="string"),
        ]
        prompt = build_report_agent_prompt(_structure(fields=fields), _template())
        # Extract content between the json code fence
        start = prompt.find("```json\n") + len("```json\n")
        end = prompt.find("\n```", start)
        json_str = prompt[start:end]
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)
        assert parsed[0]["name"] == "id"

    def test_nested_fields_are_included(self):
        children = [
            StructureField(name="city", type="string"),
            StructureField(name="country", type="string"),
        ]
        fields = [StructureField(name="address", type="object", children=children)]
        prompt = build_report_agent_prompt(_structure(fields=fields), _template())
        assert "address" in prompt
        assert "city" in prompt

    def test_prompt_contains_mustache_syntax_reference(self):
        prompt = build_report_agent_prompt(_structure(), _template())
        assert "Mustache" in prompt

    def test_prompt_contains_bootstrap_reference(self):
        prompt = build_report_agent_prompt(_structure(), _template())
        assert "Bootstrap" in prompt

    def test_selected_columns_shows_all_when_empty(self):
        structure = _structure(
            sql_query="SELECT * FROM cat.sch.tbl",
            selected_columns=[],
            tables=[StructureTable(full_name="cat.sch.tbl", alias="t")],
        )
        prompt = build_report_agent_prompt(structure, _template())
        assert "all" in prompt
