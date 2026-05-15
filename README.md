# Paginated Reporting

A full-stack web application for creating dynamic, data-driven paginated reports backed by Databricks Unity Catalog data, with AI-assisted template building and PDF export.

## Purpose

This application enables users to:
- **Organise work into Projects**: Group structures and templates, share with colleagues, and lock finalised report sets
- **Browse Unity Catalog**: Discover catalogs, schemas, and tables via a drill-down interface
- **Define Data Structures**: Select up to 3 UC tables, define PK/FK relationships, and auto-generate SQL queries with inferred nested field schemas
- **Build HTML Templates**: Design report layouts using Mustache syntax with live preview and AI assistance
- **Manage an Image Gallery**: Upload logos and assets per project and reference them in templates
- **Query Real Data**: Preview and export reports populated with data queried from Databricks SQL warehouses
- **Export to PDF**: Generate professional paginated PDF reports
- **Schedule Reports**: Define cron-based schedules to automatically render and email reports on a recurring basis
- **Deliver via Email**: Send rendered HTML or PDF reports to configured recipient lists via SMTP

## Tech Stack

### Front-End

| Technology | Purpose |
|------------|---------|
| **Vue 3** | Frontend framework with Composition API and `<script setup>` |
| **TypeScript** | Type-safe development |
| **Vite** | Fast build tool and dev server (with API proxy) |
| **Pinia** | UI state only (active project/structure/template selections) |
| **TanStack Vue Query** | Server state, data fetching, caching, and mutations |
| **Vue Router** | Client-side routing |
| **Bootstrap 5** | Responsive UI and styling |
| **Orval** | Auto-generated Vue Query composables from OpenAPI spec |
| **Axios** | HTTP client (used by Orval-generated code) |
| **Mustache.js** | Template rendering with data binding |
| **marked** | Markdown-to-HTML conversion for Markdown-type templates |
| **Vega / Vega-Lite** | Inline SVG chart rendering (bar and pie/donut) — works identically in browser preview, PDF export, and email delivery |

### Back-End

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Python async API framework |
| **Lakebase (PostgreSQL)** | Persistent storage for projects, structures, templates, images, shares, schedules, and email config |
| **Databricks SDK** | Unity Catalog discovery, workspace integration, and secret store access |
| **Databricks SQL Connector** | Querying UC tables via SQL warehouse |
| **Model Serving** | AI agent for Mustache template assistance |
| **Pydantic** | Request/response validation and domain models |
| **APScheduler** | In-process async cron scheduler for timed report execution |
| **chevron** | Server-side Mustache template rendering for scheduled reports |
| **Altair[save]** | Server-side Vega-Lite chart rendering to inline SVG for scheduled/emailed reports (bundles vl-convert-python) |
| **xhtml2pdf** | Server-side HTML-to-PDF conversion (CSS 2.1; no flexbox/grid) |
| **reportlab** | PDF primitives used by xhtml2pdf |
| **smtplib** | Standard-library SMTP client for email delivery |

## Getting Started

### Prerequisites

- Node.js 18+, npm 9+
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Databricks workspace with configured environment variables

### Back-End

```bash
cd back-end
uv sync                          # creates .venv and installs pinned deps
uv run fastapi dev app.py        # dev server on :8000
```

Dependencies are managed via `pyproject.toml`. Every package — direct and
transitive — is pinned to an exact version as a supply-chain hardening measure.
The `uv.lock` file is not committed; `uv sync` installs directly from the pins
in `pyproject.toml`. To upgrade a package, edit its pin in `pyproject.toml` and
re-run `uv sync`.

### Front-End

```bash
cd front-end
npm install
npm run dev          # dev server on :5173
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
├── app.py                          # FastAPI entry point
├── common/
│   ├── authorization.py            # Request-level auth helpers (get_user_email, is_admin, project/structure/template/schedule guards)
│   ├── authentication/             # Databricks auth (workspace, account, SQL, lakebase)
│   ├── connectors/                 # Service connectors (SQL, workspace, lakebase, model serving)
│   ├── email/
│   │   └── sender.py               # SMTP email delivery (HTML body + PDF attachment variant)
│   ├── factories/                  # App, scheduler, lakebase factories
│   ├── config.py                   # Environment configuration
│   └── logger.py                   # Shared logger
├── migrations/                     # SQL table definitions, upgrades, and seed data
├── models/                         # Pydantic domain models
│   ├── me.py                       # Me (current user info including is_admin)
│   ├── project.py                  # Project, ProjectCreate, ProjectUpdate, ProjectShare, ProjectShareCreate
│   ├── image.py                    # Image, ImageCreate, ImageUpdate
│   ├── structure.py                # Structure, StructureTable, StructureRelationship, StructureField
│   ├── template.py                 # Template
│   ├── schedule.py                 # Schedule, ScheduleCreate, ScheduleUpdate, ScheduleExecution, ExecutionStatus
│   ├── smtp_connection.py          # SmtpConnection, SmtpConnectionCreate, SmtpConnectionUpdate
│   └── email_send_list.py          # EmailSendList, EmailSendListCreate, EmailSendListUpdate
├── repositories/                   # Data access layer (Lakebase)
│   ├── projects.py                 # Project + share CRUD, user_has_access
│   ├── images.py                   # Image CRUD + binary data storage
│   ├── structures.py
│   ├── templates.py
│   ├── schedules.py                # Schedule + execution CRUD, APScheduler job sync
│   ├── smtp_connections.py         # SMTP connection CRUD
│   └── email_send_lists.py         # Send list CRUD, get_by_ids for multi-list lookups
├── services/
│   ├── agent.py                    # AI chat via Model Serving
│   ├── data_query.py               # Query UC tables for report data
│   ├── discovery.py                # Unity Catalog browsing
│   ├── query_builder.py            # Auto-generate SQL from tables + relationships
│   ├── prompt_builder.py           # Context-aware agent prompt generation
│   └── report_renderer.py          # Server-side Mustache render, SVG charts, xhtml2pdf PDF, and image inlining
└── routes/v1/
    ├── me.py                       # GET /me — current user info and admin status
    ├── projects.py                 # CRUD /projects + /projects/{id}/shares
    ├── images.py                   # CRUD /images + GET /images/{id}/data (binary serve)
    ├── structures.py               # CRUD /structures + POST /structures/{id}/build
    ├── templates.py                # CRUD /templates + preview-data + render-output
    ├── discovery.py                # GET /discovery/catalogs/.../tables/.../columns
    ├── agent.py                    # POST /agent/chat, WS /agent/ws
    ├── schedules.py                # CRUD /schedules + executions + manual run trigger
    ├── smtp_connections.py         # CRUD /smtp-connections (admin only for write operations)
    └── email_send_lists.py         # CRUD /send-lists (per-project)

front-end/
├── src/
│   ├── api/
│   │   ├── axios-instance.ts       # Axios config for API calls
│   │   └── generated/              # Orval-generated Vue Query composables + models
│   ├── components/
│   │   └── CronDescription.vue     # Human-readable cron expression display
│   ├── stores/
│   │   ├── projects.ts             # Active project state
│   │   ├── dataStructures.ts       # UI state only (activeStructureId)
│   │   └── templates.ts            # UI state only (activeTemplateId)
│   └── views/
│       ├── ProjectsView.vue        # Project management (create, open, lock, share)
│       ├── ImagesView.vue          # Image gallery (upload, rename, copy URL, delete)
│       ├── DataStructuresView.vue
│       ├── TemplateEditorView.vue
│       ├── SchedulesView.vue       # Schedule management (create, edit, toggle, run, view executions)
│       └── SettingsView.vue        # Admin: SMTP connections and email send lists
├── orval.config.ts                 # Orval API generation config
└── vite.config.ts                  # Vite with API proxy
```

## Security Model

### User Identity

User identity is derived from the `X-Forwarded-Email` header injected by the Databricks Apps runtime. The `get_user_email()` helper in `common/authorization.py` reads this header on every request. In local development (`ENV=DEV`), it falls back to a fixed dev email if the header is absent.

### Admin Authorization

Some operations (managing SMTP connections) are restricted to admin users. Admins are defined by the `ADMIN_EMAILS` environment variable — a comma-separated list of email addresses. The `is_admin(email)` helper checks membership, and the `require_admin` FastAPI dependency raises `403` for non-admins. The `AdminUser` annotated type is used in route signatures to enforce this automatically.

The `/api/v1/me` endpoint returns an `is_admin` boolean so the front-end can conditionally show admin-only UI.

### Authorization Guards

`common/authorization.py` provides a set of reusable async guard functions used by route handlers:

| Guard | Effect |
|-------|--------|
| `get_user_email(request)` | Extracts user email; raises `401` if missing |
| `is_admin(email)` | Returns `True` if the email is in `ADMIN_EMAILS` |
| `require_admin(email)` | Raises `403` if the user is not an admin |
| `check_project_access(project_id, email)` | Raises `403` if user is not owner or a shared member |
| `check_project_not_locked(project_id)` | Raises `423` if the project is locked |
| `check_structure_read_access(structure_id, email)` | Access check via the structure's project |
| `check_structure_project_not_locked(structure_id)` | Lock check via the structure's project |
| `check_structure_project_access(structure_id, email)` | Access + lock check via the structure's project |
| `check_template_read_access(template_id, email)` | Access check via template → structure → project |
| `check_template_project_not_locked(template_id)` | Lock check via template → structure → project |
| `check_template_project_access(template_id, email)` | Access + lock check via template → structure → project |
| `check_schedule_project_access(schedule_id, email)` | Access + lock check via schedule → project |

### Project Ownership and Sharing

Every project has an `owner` (the user who created it). Access is granted to the owner and any users listed in the `project_shares` table.

| Action | Owner | Shared user |
|--------|-------|-------------|
| View structures & templates | Yes | Yes |
| Create / edit / delete structures & templates | Yes (if unlocked) | Yes (if unlocked) |
| Lock / unlock project | Yes | No |
| Add / remove shares | Yes | No |
| Rename project | Yes | No |
| Delete project | Yes | No |

### Project Locking

Any project can be locked by its owner. While locked, all mutating operations (create, update, delete) on the project's structures, templates, and images return `423 Locked`. Read operations are always permitted.

### Image Security

Images are stored as base64-encoded blobs in Lakebase and served via `GET /api/v1/images/{id}/data`. Each request validates that the requesting user has access to the image's project before serving the binary. Images are served with:

- `Cache-Control: public, max-age=86400` — 24-hour browser caching for fast previews
- `Content-Security-Policy: default-src 'none'` — prevents any embedded scripts from executing

Upload restrictions:
- Allowed MIME types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml`
- Maximum file size: **2 MB**
- Maximum images per project: **20**

## How to Use the App

The app has eight main sections accessible from the sidebar: **Home**, **Projects**, **Data Structures**, **Template Editor**, **Preview**, **Image Gallery**, **Schedules**, and **Settings** (admin only).

### Step 0 — Create a Project

Navigate to **Projects** and click **New Project**. Give it a name and click **Open** to set it as active. All structures and templates you create will be associated with this project.

You can share the project with colleagues (by email), lock it to prevent edits, and filter all views to show only the active project's data.

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

#### Template types

When creating a template, choose between **HTML** (default) or **Markdown**:

- **HTML** — full Bootstrap 5 layout, custom CSS, `.report-page` divs, and page break control. Best for complex multi-column designs.
- **Markdown** — write GitHub Flavoured Markdown (headings, bold, tables, lists) combined with Mustache syntax. The server and preview both render Markdown via `marked`. Best for text-heavy reports where layout complexity is low. Inline HTML (including page-break divs) is supported inside Markdown templates.

#### Page size (output format)

Each template has a **Page Size** setting toggled in the editor toolbar:

| Setting | Output | Scheduled delivery | Manual export |
|---------|--------|--------------------|---------------|
| **Email** (default) | Self-contained HTML | Inline HTML email | Download HTML button |
| **A4 (PDF)** *(Experimental)* | PDF attachment | PDF email attachment | Download PDF via `/render-output` |

When set to **A4**, the server renders the report to PDF using **xhtml2pdf** (CSS 2.1 only). This means flexbox, CSS grid, gradients, and `box-shadow` are **not** supported in PDF output — use tables and simple block layouts for best results. Charts are pre-rendered to SVG before PDF conversion.

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

Use `.report-page` divs and pagination magic commands (available in the Insert Component palette and documented in the Guide) to control pagination.

### Step 3 — Upload Images (optional)

Navigate to **Image Gallery** (requires an active project). Upload logos or assets — drag & drop or click **Upload**. Click the link icon on any image card to copy an `img:UUID` reference for use in templates — e.g. `<img src="img:IMAGE_ID" alt="Logo" />`.

### Step 4 — Preview & Export

Navigate to **Preview** and select your template from the dropdown. The app fetches real data from your Databricks SQL warehouse, renders it through the template, and displays the paginated result.

The preview fetches up to **50 rows** by default — use the **Preview rows** input in the preview toolbar to increase or decrease this (1–10 000). Charts are rendered as inline SVG in the preview so they look identical to the exported output.

The export action depends on the template's **Page Size** setting:

- **Email templates** — click **Download HTML** to download a self-contained `.html` file with all images and charts inlined. The server renders the full dataset, renders charts as SVG, and inlines all image references as base64 data URIs so the file opens standalone.
- **A4 (PDF) templates** — click **Export / Print PDF** to open the browser print dialog, or use `GET /api/v1/templates/{id}/render-output` to download a server-rendered `.pdf` file generated by xhtml2pdf.

### Step 5 — Schedule Automated Delivery

Navigate to **Schedules** and click **New Schedule** (requires an active project).

1. Give the schedule a name and select the template to render.
2. Enter a 5-field cron expression (e.g. `0 8 * * 1` for every Monday at 8 AM). A human-readable description is shown below the field.
3. Optionally attach one or more **send lists** — the report will be emailed to all recipients in those lists on each run.
4. Toggle **Active** to enable or disable the schedule without deleting it.
5. Use the **Run now** button to trigger a manual execution immediately.

The **Executions** panel on each schedule card shows the history of runs with status (`pending` / `running` / `success` / `failed`) and any error messages.

Scheduled reports are rendered server-side using the app's service principal credentials — no user token is required at execution time.

### Step 6 — Configure Email (Admin Only)

Admins (users listed in `ADMIN_EMAILS`) have access to the **Settings** page. Here you can manage:

#### SMTP Connections

Click **New Connection** to add an SMTP server. Supported providers have defaults pre-filled (Gmail / G Suite, SendGrid). The password is stored in Databricks Secrets (scope configured by `SMTP_SECRET_SCOPE`) — it is never stored in Lakebase.

You cannot delete an SMTP connection that is referenced by an active send list — remove or reassign those lists first.

#### Email Send Lists

Send lists are per-project groups of email recipients linked to an SMTP connection. Create a send list, enter recipient email addresses, and attach it to one or more schedules. When a scheduled report runs, it sends the rendered HTML email (or PDF attachment) to all addresses in the attached lists.

### Reference: the Guide

The **Guide** page (accessible from the sidebar) contains a full reference for:

- Projects — ownership, sharing, locking, and permissions
- Mustache syntax patterns
- Flat tables, struct fields, and arrays of structs
- Markdown templates — GFM syntax, tables, and Mustache integration
- Building bar and pie charts from Unity Catalog data (inline SVG — works in PDF, email, and browser)
- Conditional styling using SQL-derived boolean columns
- Images — uploading, referencing, and limitations
- **Pagination Magic** — page breaks, page-break-before, no-break, data-break-after, repeating headers/footers, and multi-column layouts

---

## Key Workflows

1. **Create a project** -- Organise your work; share and lock as needed
2. **Discover data** -- Browse Unity Catalog to find tables
3. **Define structure** -- Select up to 3 tables, define PK/FK relationships, and build to auto-generate SQL and infer nested fields
4. **Create template** -- Write Mustache HTML, use AI agent for help, reference uploaded images
5. **Preview** -- Fetches limited real data from the structure's auto-generated query
6. **Export** -- Fetches full dataset and renders to HTML (email) or PDF (A4, experimental)
7. **Schedule** -- Define cron schedules to auto-render and email reports; track execution history
8. **Configure email** (admin) -- Set up SMTP connections and per-project send lists

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

## Key Environment Variables (back-end/.env)

```
ENV=DEV                           # Enables CORS and dev user fallback for local development
DATABRICKS_HOST=                  # Workspace URL
DATABRICKS_TOKEN=                 # PAT (or use DATABRICKS_CLIENT_ID/SECRET)
DATABRICKS_WAREHOUSE_ID=          # SQL Warehouse for data queries
LAKEBASE_ENDPOINT=                # Full endpoint resource path — see Lakebase setup below
PGDATABASE=databricks_postgres    # Postgres database name
PGUSER=                           # Service principal client ID (DB username)
PGPORT=5432
PGSSLMODE=require
LAKEBASE_SCHEMA=app               # Schema name (default: app)
MODEL_SERVING_ENDPOINT=           # Defaults to databricks-claude-sonnet-4-6
LAKEHOUSE_CATALOG_NAME=           # Unity Catalog catalog for data discovery
LAKEHOUSE_SCHEMA_NAME=            # Unity Catalog schema for data discovery
ADMIN_EMAILS=                     # Comma-separated list of admin user emails (can manage SMTP connections)
SMTP_SECRET_SCOPE=paginated-reports-smtp  # Databricks Secret scope for SMTP passwords (default shown)
```

## Lakebase Autoscaling Postgres Setup

The app uses **Databricks Lakebase Autoscaling Postgres** (the new `w.postgres` SDK) for persistent storage. The DABs postgres app resource is intentionally bypassed — it requires an opaque auto-generated database ID (`db-8uv1-...`) that cannot be predicted at bundle authoring time. Instead, connection details are passed as explicit env vars.

### 1. Deploy the DABs resources

```bash
databricks bundle deploy --target dev
```

This creates the Lakebase project (`paginated-reports-project`), branch (`main`), SQL warehouse, catalog, and schema. It does **not** create a Postgres role for the app's service principal — that is done in step 3.

### 2. Find the endpoint resource path

```bash
databricks postgres endpoints list --parent projects/paginated-reports-project/branches/main
```

Copy the `name` field (e.g. `projects/paginated-reports-project/branches/main/endpoints/primary`) and set it as `lakebase_endpoint` in the relevant target in `databricks.yml`.

### 3. Create the Postgres role for the app service principal

Because the postgres app resource is bypassed, DABs cannot auto-create a Postgres role for the app's SP. Run this **once** as the project owner (in a Databricks notebook) before the app first connects:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.postgres import (
    Role, RoleRoleSpec, RoleIdentityType, RoleAuthMethod
)

w = WorkspaceClient()

APP_SP_CLIENT_ID = "<app-service-principal-client-id>"  # visible in App settings page
BRANCH = "projects/paginated-reports-project/branches/main"

w.postgres.create_role(
    parent=BRANCH,
    role=Role(spec=RoleRoleSpec(
        identity_type=RoleIdentityType.SERVICE_PRINCIPAL,
        auth_method=RoleAuthMethod.LAKEBASE_OAUTH_V1,
        postgres_role=APP_SP_CLIENT_ID,
    )),
    role_id=APP_SP_CLIENT_ID,
).wait()
print("Role created")
```

Then grant database access (connect as your owner identity via psql or a notebook):

```sql
GRANT ALL ON DATABASE databricks_postgres TO "<app-service-principal-client-id>";
GRANT ALL ON SCHEMA app TO "<app-service-principal-client-id>";
```

### 4. Deploy the app

```bash
databricks bundle deploy --target dev   # picks up the lakebase_endpoint variable
```

On startup the app will:
1. Call `w.postgres.get_endpoint(name=LAKEBASE_ENDPOINT)` to resolve the DNS hostname from `endpoint.status.hosts.host`
2. Generate an initial OAuth token via `w.postgres.generate_database_credential(endpoint=...)`
3. Run database migrations
4. Start a background task that refreshes the token before it expires (tokens last 1 hour; refresh is scheduled using the `expire_time` returned by the API)

### How authentication works

OAuth tokens are generated per-connection using the app's service principal credentials — no long-lived passwords are stored. The `LakebaseAuthentication` class in `common/authentication/lakebase.py` manages token lifecycle. The SQLAlchemy `do_connect` event injects the current token as the Postgres password on every new connection.

## License

MIT
