# Paginated Reporting

A full-stack web application for creating dynamic, data-driven paginated reports backed by Databricks Unity Catalog data, with AI-assisted template building and PDF export.

## Purpose

This application enables users to:
- **Browse Unity Catalog**: Discover catalogs, schemas, and tables via a drill-down interface
- **Define Data Structures**: Select up to 3 UC tables, define PK/FK relationships, and auto-generate SQL queries with inferred nested field schemas
- **Build HTML Templates**: Design report layouts using Mustache syntax with live preview and AI assistance
- **Query Real Data**: Preview and export reports populated with data queried from Databricks SQL warehouses
- **Export to PDF**: Generate professional paginated PDF reports

## Tech Stack

### Front-End

| Technology | Purpose |
|------------|---------|
| **Vue 3** | Frontend framework with Composition API and `<script setup>` |
| **TypeScript** | Type-safe development |
| **Vite** | Fast build tool and dev server (with API proxy) |
| **Pinia** | UI state only (active selections); no server data |
| **TanStack Vue Query** | Server state, data fetching, caching, and mutations |
| **Vue Router** | Client-side routing |
| **Bootstrap 5** | Responsive UI and styling |
| **Orval** | Auto-generated Vue Query composables from OpenAPI spec |
| **Axios** | HTTP client (used by Orval-generated code) |
| **Mustache.js** | Template rendering with data binding |
| **Chart.js + vue-chartjs** | Interactive charts |
| **html2pdf.js** | Client-side PDF generation |

### Back-End

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Python async API framework |
| **Lakebase (PostgreSQL)** | Persistent storage for structures, templates, and conversations |
| **Databricks SDK** | Unity Catalog discovery and workspace integration |
| **Databricks SQL Connector** | Querying UC tables via SQL warehouse |
| **Model Serving** | AI agent for Mustache template assistance |
| **Pydantic** | Request/response validation and domain models |

## Getting Started

### Prerequisites

- Node.js 18+, npm 9+
- Python 3.11+
- Databricks workspace with configured environment variables

### Back-End

```bash
cd back-end
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Front-End

```bash
cd front-end
npm install
npm run dev
```

The front-end proxies `/api` requests to `http://localhost:8000` in development.

### Regenerate API Client

When backend routes change, regenerate the typed API client:

```bash
cd front-end
npm run generate-all
```

## Architecture

```
back-end/
├── app.py                       # FastAPI entry point
├── common/
│   ├── authentication/          # Databricks auth (workspace, account, SQL, lakebase)
│   ├── connectors/              # Service connectors (SQL, workspace, lakebase, model serving)
│   ├── factories/               # App, scheduler, lakebase factories
│   ├── config.py                # Environment configuration
│   └── logger.py                # Shared logger
├── migrations/                  # SQL table definitions, upgrades, and seed data
├── models/                      # Pydantic domain models
│   ├── structure.py             # Structure, StructureTable, StructureRelationship, StructureField
│   └── template.py              # Template (HTML-only, no sql_query)
├── repositories/                # Data access layer (Lakebase)
│   ├── structures.py
│   └── templates.py
├── services/
│   ├── agent.py                 # AI chat via Model Serving
│   ├── data_query.py            # Query UC tables for report data (uses structure.sql_query)
│   ├── discovery.py             # Unity Catalog browsing
│   ├── query_builder.py         # Auto-generate SQL from tables + relationships, infer fields
│   └── prompt_builder.py        # Context-aware agent prompt generation
└── routes/v1/
    ├── structures.py            # CRUD /structures + POST /structures/{id}/build
    ├── templates.py             # CRUD /templates + preview-data/report-data
    ├── discovery.py             # GET /discovery/catalogs/.../tables/.../columns
    └── agent.py                 # POST /agent/chat, WS /agent/ws

front-end/
├── src/
│   ├── api/
│   │   ├── axios-instance.ts    # Axios config for API calls
│   │   └── generated/           # Orval-generated Vue Query composables + models
│   ├── stores/
│   │   ├── dataStructures.ts    # UI state only (activeStructureId)
│   │   └── templates.ts         # UI state only (activeTemplateId)
│   └── views/
│       ├── DiscoveryView.vue    # UC catalog/schema/table browser
│       ├── DataStructuresView.vue
│       ├── TemplateEditorView.vue
│       └── PreviewView.vue
├── orval.config.ts              # Orval API generation config
└── vite.config.ts               # Vite with API proxy
```

## How to Use the App

The app has four main sections accessible from the sidebar: **Home**, **Data Structures**, **Template Editor**, and **Preview**.

### Step 1 — Define a Data Structure

Navigate to **Data Structures** and click **New Structure**.

1. Give your structure a name.
2. Browse the Unity Catalog tree (Catalog → Schema → Table) and select the table(s) you want to report on — up to 3 tables in a linear chain.
3. Define PK/FK relationships between tables if using more than one.
4. Click **Save & Build** — the app auto-generates a SQL query and infers a nested field schema from the selected columns and their types (including `ARRAY` and `STRUCT` fields).

The inferred fields determine the Mustache variables available in your templates.

### Step 2 — Build a Template

Navigate to **Template Editor** and click the **+** button to create a new template, linking it to the structure you just built.

The editor has two panels:

- **Left** — a CodeMirror HTML editor where you write Mustache-flavoured HTML
- **Right** — a live preview rendered against your structure's schema

Useful tools in the editor:

| Tool | What it does |
|------|-------------|
| **Insert Component** | Drop in pre-built snippets: tiles, tables, bar/pie charts, page breaks, status badges, and paginated sections |
| **Data Structure Hint** | Shows the inferred field names and types available in `{{mustache}}` syntax |
| **Mustache Help** | Quick reference for `{{field}}`, `{{#section}}`, `{{^inverted}}`, and dot notation |
| **Format HTML** | Auto-formats your markup |
| **AI Assistant** | Context-aware chat panel — aware of your structure, fields, and template — to help write or debug Mustache |

Templates auto-save as you type. Use **Save** to save manually, or **Delete** to remove a template.

#### Mustache basics

```html
<!-- Scalar field -->
<p>{{customer_name}}</p>

<!-- Loop over a nested array -->
{{#orders}}
  <p>{{order_id}} — {{total}}</p>
{{/orders}}

<!-- Conditional visibility -->
{{#is_overdue}}<span class="badge bg-danger">Overdue</span>{{/is_overdue}}
```

Use `.report-page` divs and `<!-- PAGE BREAK -->` comments (available in the Insert Component palette) to control pagination.

### Step 3 — Preview & Export

Navigate to **Preview** and select your template from the dropdown. The app fetches real data from your Databricks SQL warehouse, renders it through the template, and displays the paginated result.

Click **Export / Print PDF** to open the browser print dialog. Print media styles hide the toolbar so only the report content is printed. Configure your browser to print to PDF for a clean output.

### Reference: the Guide

The **Guide** page (accessible from the sidebar) contains a full reference for:

- Mustache syntax patterns
- Flat tables, struct fields, and arrays of structs
- Building bar and pie charts from Unity Catalog data
- Conditional styling using SQL-derived boolean columns

---

## Key Workflows

1. **Discover data** -- Browse Unity Catalog to find tables
2. **Define structure** -- Select up to 3 tables, define PK/FK relationships (linear chain), and build to auto-generate SQL and infer nested fields
3. **Create template** -- Write Mustache HTML, use AI agent for help
4. **Preview** -- Fetches limited real data from the structure's auto-generated query
5. **Export** -- Fetches full dataset and renders paginated PDF

## Data Structure Design

### How fields are inferred

When you click **Save & Build**, the app fetches column metadata from Unity Catalog for every selected column and maps each `type_text` string recursively to a `StructureField` tree:

| UC type | Inferred field type | Mustache behaviour |
|---------|--------------------|--------------------|
| `STRING`, `VARCHAR`, … | `string` | `{{field}}` |
| `INT`, `BIGINT`, `DOUBLE`, … | `number` | `{{field}}` |
| `BOOLEAN` | `boolean` | `{{#field}}…{{/field}}` |
| `DATE`, `TIMESTAMP` | `date` | `{{field}}` |
| `STRUCT<a:string, b:int>` | `object` with children | `{{field.a}}` / push context with `{{#field}}` |
| `ARRAY<STRUCT<…>>` | `array` with children | `{{#field}}…{{/field}}` iterates items |
| `ARRAY<scalar>` | `array` (no children) | treated as a plain value |
| `MAP<…>` | `object` (no children) | treated as a plain value |

### The `rows` wrapper and the array assumption

Every query result is wrapped in a top-level `rows` array before being passed to Mustache:

```json
{
  "rows": [
    { "customer_id": 1, "name": "Alice", "_index": 1, "_total": 3 },
    { "customer_id": 2, "name": "Bob",   "_index": 2, "_total": 3 },
    { "customer_id": 3, "name": "Carol", "_index": 3, "_total": 3 }
  ]
}
```

This means **every template must open with `{{#rows}}`** and close with `{{/rows}}`:

```html
{{#rows}}
  <p>{{name}}</p>
{{/rows}}
```

Two special fields are injected into every row automatically:

| Field | Value |
|-------|-------|
| `{{_index}}` | 1-based position of this row |
| `{{_total}}` | total number of rows returned |

### Nested columns (STRUCT and ARRAY\<STRUCT\>)

`ARRAY<STRUCT<…>>` columns are returned as native Python lists by the Databricks Arrow deserialiser — no additional mapping is needed. They appear as nested arrays inside each row and can be iterated directly:

```html
{{#rows}}
  <h2>{{order_id}}</h2>
  <!-- line_items is ARRAY<STRUCT<product:string, qty:int>> -->
  {{#line_items}}
    <p>{{product}} × {{qty}}</p>
  {{/line_items}}
{{/rows}}
```

`STRUCT` columns are returned as dicts. Use dot notation or a context-push to access sub-fields:

```html
{{customer.first_name}}        {{! dot notation }}

{{#customer}}                  {{! context push }}
  {{first_name}} {{last_name}}
{{/customer}}
```

### Type mapping summary

```
UC column                          → StructureField
─────────────────────────────────────────────────────────────────────
order_id         INT               → { name: "order_id",   type: "number" }
status           STRING            → { name: "status",     type: "string" }
placed_at        TIMESTAMP         → { name: "placed_at",  type: "date"   }
address          STRUCT<street:    → { name: "address",    type: "object",
                   string,              children: [
                   city:string>            { name: "street", type: "string" },
                                          { name: "city",   type: "string" }
                                        ]
                                   }
line_items       ARRAY<STRUCT<     → { name: "line_items", type: "array",
                   product:string,      children: [
                   qty:int>>               { name: "product", type: "string" },
                                          { name: "qty",     type: "number" }
                                        ]
                                   }
```

Structures own the data definition:
- **Tables**: Up to 3 UC tables selected via discovery (linear chain only)
- **Relationships**: PK/FK 1-to-many links between tables (A → B → C)
- **SQL Query**: Auto-generated from tables + relationships (not user-editable)
- **Fields**: Auto-inferred from UC column metadata, nested based on relationships

Templates are pure HTML -- they reference a structure and render its data using Mustache syntax.