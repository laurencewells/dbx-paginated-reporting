"""Synthetic test data for report renderer tests.

All field values are fabricated. Use these fixtures instead of any real
customer template/data to keep the test suite self-contained and committable.
"""
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

# Deterministic UUID for the synthetic logo image referenced in kpi_synthetic_template.html.
LOGO_UUID = "00000000-0000-0000-0000-000000000001"


def _load(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


SUPPLIER_TEMPLATE = _load("supplier_template.html")
KPI_TEMPLATE = _load("kpi_synthetic_template.html")


# ---------------------------------------------------------------------------
# Supplier rows — fabricated; nested arrays exercise {{#top_5_customers}} and
# the empty-array {{^top_5_customers}} fallback path.
# ---------------------------------------------------------------------------

SUPPLIER_ROWS = [
    {
        "_index": 1,
        "_total": 2,
        "supplier_name": "ACME Corp",
        "supplierID": "S001",
        "supplier_continent": "Europe",
        "supplier_city": "London",
        "total_transactions": 1250,
        "total_sales_amount": 487500,
        "top_5_customers": [
            {"customer_name": "Widget Co", "transactions": 200, "amount": 85000},
            {"customer_name": "Gadget Inc", "transactions": 180, "amount": 72000},
        ],
        "top_3_products": [
            {"product": "Widget A", "transactions": 400, "amount": 160000},
        ],
    },
    {
        "_index": 2,
        "_total": 2,
        "supplier_name": "Global Trade Ltd",
        "supplierID": "S002",
        "supplier_continent": "Asia",
        "supplier_city": "Tokyo",
        "total_transactions": 980,
        "total_sales_amount": 392000,
        "top_5_customers": [],
        "top_3_products": [],
    },
]


# ---------------------------------------------------------------------------
# KPI rows — fabricated regional performance metrics.
#
# Each section is introduced by a row with metric_name="" (renders as section
# header via {{^metric_name}}). Following rows have metric_name set and render
# as data rows via {{#metric_name}}.
# ---------------------------------------------------------------------------

KPI_ROWS = [
    {
        "section": "REVENUE",
        "metric_name": "",  # section header row
        "report_date": "2026-04-30",
        "region": "",
        "current_value": "",
        "current_value_raw": "",
        "target_value": "",
        "vs_target_pct": "",
        "vs_target_color": "",
        "prior_value": "",
        "vs_prior_pct": "",
        "vs_prior_color": "",
    },
    {
        "section": "",
        "metric_name": "Net Revenue",
        "report_date": "2026-04-30",
        "region": "North",
        "current_value": "$720K",
        "current_value_raw": 720000,
        "target_value": "$700K",
        "vs_target_pct": "+2.9%",
        "vs_target_color": "var-positive",
        "prior_value": "$680K",
        "vs_prior_pct": "+5.9%",
        "vs_prior_color": "var-positive",
    },
    {
        "section": "",
        "metric_name": "Gross Margin",
        "report_date": "2026-04-30",
        "region": "South",
        "current_value": "$310K",
        "current_value_raw": 310000,
        "target_value": "$320K",
        "vs_target_pct": "-3.1%",
        "vs_target_color": "var-negative",
        "prior_value": "$295K",
        "vs_prior_pct": "+5.1%",
        "vs_prior_color": "var-positive",
    },
]


def kpi_context_with_first() -> dict:
    """Return a {rows, _first} dict as DataQueryService._map_results_to_data produces.

    _first contains the first row's scalar values (excluding _index/_total/_even).
    """
    rows_enriched = [
        dict(row, _index=i + 1, _total=len(KPI_ROWS), _even=((i + 1) % 2 == 0))
        for i, row in enumerate(KPI_ROWS)
    ]
    scalar_types = (str, int, float, bool, type(None))
    _first = {
        k: v
        for k, v in KPI_ROWS[0].items()
        if k not in ("_index", "_total", "_even") and isinstance(v, scalar_types)
    }
    return {"rows": rows_enriched, "_first": _first}
