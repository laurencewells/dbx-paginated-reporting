"""
Server-side report renderer for scheduled executions.

Executes the structure's SQL query against the Databricks SQL warehouse,
builds the Mustache context, and renders the template HTML using chevron.
No user bearer token is available in scheduled context — the app's service
principal credentials (from environment) are used by SQLConnector by default.
"""

from uuid import UUID

import chevron

from common.connectors.sql import SQLConnector
from common.logger import log as L
from repositories.structures import StructuresRepository
from repositories.templates import TemplatesRepository
from services.data_query import DataQueryService


async def render_report(template_id: UUID) -> str:
    """
    Render a report template server-side using the app's service principal.

    Returns the fully rendered HTML string.
    Raises ValueError if the template or structure cannot be found.
    Raises RuntimeError on query or rendering failure.
    """
    templates_repo = TemplatesRepository()
    structures_repo = StructuresRepository()

    template = await templates_repo.get_by_id(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    structure = await structures_repo.get_by_id(template.structure_id)
    if not structure:
        raise ValueError(f"Structure {template.structure_id} not found")

    if not structure.sql_query:
        L.warning(f"[ReportRenderer] Template {template_id} has no SQL query — rendering empty")
        context: dict = {"rows": []}
    else:
        try:
            # No bearer token — relies on the service principal env credentials
            svc = DataQueryService(sql_connector=SQLConnector())
            result = await svc.execute_for_preview(template_id, limit=10000)
            context = result.get("data", {"rows": []})
        except Exception as e:
            raise RuntimeError(f"Failed to execute query for template {template_id}: {e}") from e

    try:
        rendered = chevron.render(template.html_content, context)
    except Exception as e:
        raise RuntimeError(f"Failed to render template {template_id}: {e}") from e

    return rendered
