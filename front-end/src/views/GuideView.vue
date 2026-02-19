<script setup lang="ts">
import { ref } from 'vue'

const activeSection = ref('projects')

const sections = [
  { id: 'projects',          label: 'Projects',            icon: 'bi-folder2-open' },
  { id: 'mustache',          label: 'Mustache Syntax',    icon: 'bi-braces' },
  { id: 'flat-table',        label: 'Flat Table',          icon: 'bi-table' },
  { id: 'struct',            label: 'Struct Fields',       icon: 'bi-braces-asterisk' },
  { id: 'array-struct',      label: 'Array of Structs',    icon: 'bi-list-nested' },
  { id: 'chart-struct',      label: 'Charts from Structs', icon: 'bi-bar-chart' },
  { id: 'conditional-styles',label: 'Conditional Styles',  icon: 'bi-palette' },
  { id: 'images',            label: 'Images',              icon: 'bi-images' },
]

// ── Inline syntax tags ────────────────────────────────────────────────────────
const t = {
  variable:       '{{field}}',
  triple:         '{{{field}}}',
  section:        '{{#section}}...{{/section}}',
  inverted:       '{{^section}}...{{/section}}',
  dot:            '{{.}}',
  comment:        '{{! comment }}',
  ex_field:       '{{cluster_name}}',
  ex_dot_loop:    '{{#tags}}{{.}}{{/tags}}',
  ex_comment:     '{{! TODO: add chart }}',
  rows_open:      '{{#rows}}',
  rows_close:     '{{/rows}}',
  rows_wrong:     '{{/#}}',
  delete_check:        '{{^delete_time}}Active{{/delete_time}}',
  index:               '{{_index}}',
  total:               '{{_total}}',
  address_city:        '{{address.city}}',
  address_open:        '{{#address}}',
  address_close:       '{{/address}}',
  cond_class_example:  'status-{{approval_status}}',
  cond_bool_sql:       "approval_status = 'approved' AS is_approved",
  cond_bool_section:   '{{#is_approved}}...{{/is_approved}}',
}

// ── Large code blocks ─────────────────────────────────────────────────────────

const code = {
  dataShape: `{
  "rows": [
    { "field1": "value", "field2": 42 },
    { "field1": "value", "field2": 99 }
  ]
}`,

  flatTable_sql: `-- system.compute.clusters (example)
cluster_name   VARCHAR
cluster_id     VARCHAR
owned_by       VARCHAR
worker_count   INT
create_time    TIMESTAMP
delete_time    TIMESTAMP   -- NULL if still active`,

  flatTable_data: `{
  "rows": [
    {
      "cluster_name": "ml-team-gpu",
      "cluster_id": "0120-123456-abc",
      "owned_by": "user@example.com",
      "worker_count": 4,
      "create_time": "2024-01-15T10:30:00",
      "delete_time": null,
      "_index": 1,
      "_total": 42
    },
    ...
  ]
}`,

  flatTable_template: `<div class="report-page">
  <div class="p-4">
    <h1 class="fw-bold text-primary">Cluster Report</h1>
    <hr>

    <table class="report-table table table-striped">
      <thead>
        <tr>
          <th>Cluster Name</th>
          <th>Owner</th>
          <th>Workers</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {{#rows}}
        <tr>
          <td class="fw-semibold">{{cluster_name}}</td>
          <td>{{owned_by}}</td>
          <td><span class="badge bg-primary">{{worker_count}}</span></td>
          <td>
            {{^delete_time}}<span class="badge bg-success">Active</span>{{/delete_time}}
            {{#delete_time}}<span class="badge bg-danger">Terminated</span>{{/delete_time}}
          </td>
        </tr>
        {{/rows}}
        {{^rows}}
        <tr><td colspan="4" class="text-center text-muted py-4">No data</td></tr>
        {{/rows}}
      </tbody>
    </table>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>`,

  struct_sql: `-- employee table
name          VARCHAR
department    VARCHAR
address       STRUCT<
                city:    VARCHAR,
                country: VARCHAR,
                zip:     VARCHAR
              >`,

  struct_data: `{
  "rows": [
    {
      "name": "Alice",
      "department": "Engineering",
      "address": {
        "city": "London",
        "country": "UK",
        "zip": "EC1A 1BB"
      }
    }
  ]
}`,

  struct_context: `{{#rows}}
  <td>{{name}}</td>

  {{#address}}
    <td>{{city}}</td>
    <td>{{country}}</td>
    <td>{{zip}}</td>
  {{/address}}
{{/rows}}`,

  struct_dot: `{{#rows}}
  <td>{{name}}</td>
  <td>{{address.city}}</td>
  <td>{{address.country}}</td>
  <td>{{address.zip}}</td>
{{/rows}}`,

  array_sql: `-- order table
order_id      VARCHAR
customer      VARCHAR
items         ARRAY<STRUCT<
                product: VARCHAR,
                qty:     INT,
                price:   DOUBLE
              >>`,

  array_data: `{
  "rows": [
    {
      "order_id": "ORD-001",
      "customer": "Acme Corp",
      "items": [
        { "product": "Widget A", "qty": 3, "price": 9.99 },
        { "product": "Widget B", "qty": 1, "price": 24.99 }
      ]
    }
  ]
}`,

  array_template: `{{#rows}}
<div class="report-page">
  <div class="p-4">
    <h2>Order: {{order_id}}</h2>
    <p class="text-muted">Customer: {{customer}}</p>

    <table class="report-table table">
      <thead>
        <tr>
          <th>Product</th>
          <th>Qty</th>
          <th>Unit Price</th>
        </tr>
      </thead>
      <tbody>
        {{#items}}
        <tr>
          <td>{{product}}</td>
          <td>{{qty}}</td>
          <td>£{{price}}</td>
        </tr>
        {{/items}}
      </tbody>
    </table>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>
{{/rows}}`,

  chart1_template: `<!-- SQL: SELECT region, SUM(revenue) as total FROM sales GROUP BY region -->

<div class="chart-container">
  <div class="chart-title">Revenue by Region</div>
  <div class="report-bar-chart"
    data-labels="{{#rows}}{{region}},{{/rows}}"
    data-values="{{#rows}}{{total}},{{/rows}}">
  </div>
</div>`,

  chart2_template: `<!-- SQL: SELECT active_count, terminated_count FROM cluster_summary -->

<div class="chart-container">
  <div class="chart-title">Cluster Status</div>
  <div class="report-pie-chart"
    data-labels="Active,Terminated"
    data-values="{{#rows}}{{active_count}},{{terminated_count}}{{/rows}}">
  </div>
</div>`,

  chart3_sql: `SELECT
  team_name,
  headcount,
  -- pre-aggregate monthly spend into an array
  array_agg(
    named_struct('month', month_name, 'spend', monthly_spend)
    ORDER BY month_num
  ) AS spend_by_month
FROM team_metrics
GROUP BY team_name, headcount`,

  chart3_data: `{
  "rows": [
    {
      "team_name": "Engineering",
      "headcount": 24,
      "spend_by_month": [
        { "month": "Jan", "spend": 48000 },
        { "month": "Feb", "spend": 52000 },
        { "month": "Mar", "spend": 51000 }
      ]
    }
  ]
}`,

  conditional_sql_pattern1: `-- No changes needed — use the field value directly as a CSS class
SELECT
  supplier_name,
  approval_status,   -- e.g. 'approved', 'pending', 'rejected'
  category,
  onboarded_date
FROM procurement.suppliers`,

  conditional_template_pattern1: `<style>
  /* Class name = "status-" + the field value */
  .status-approved { background-color: #198754; color: white; }
  .status-pending  { background-color: #fd7e14; color: white; }
  .status-rejected { background-color: #dc3545; color: white; }
</style>

{{#rows}}
<div class="report-page">
  <div class="report-page-header d-flex justify-content-between align-items-center">
    <h2>{{supplier_name}}</h2>
    <span class="badge fs-6 status-{{approval_status}}">{{approval_status}}</span>
  </div>

  <div class="row mb-4">
    <div class="col-md-6">
      <p class="text-muted mb-1">Category</p>
      <p class="fw-semibold">{{category}}</p>
    </div>
    <div class="col-md-6">
      <p class="text-muted mb-1">Onboarded</p>
      <p class="fw-semibold">{{onboarded_date}}</p>
    </div>
  </div>

  <div class="page-number">Supplier {{_index}} of {{_total}}</div>
</div>
{{/rows}}`,

  conditional_sql_pattern2: `-- Add boolean columns in SQL for full block conditionals
SELECT
  supplier_name,
  approval_status,
  category,
  onboarded_date,
  approval_status = 'approved' AS is_approved,
  approval_status = 'pending'  AS is_pending,
  approval_status = 'rejected' AS is_rejected
FROM procurement.suppliers`,

  conditional_template_pattern2: `{{#rows}}
<div class="report-page">
  <div class="report-page-header">
    <h2>{{supplier_name}}</h2>
  </div>

  {{#is_approved}}
  <div class="alert alert-success">
    <i class="bi bi-check-circle-fill me-2"></i>
    This supplier is <strong>approved</strong> and active.
  </div>
  {{/is_approved}}

  {{#is_pending}}
  <div class="alert alert-warning">
    <i class="bi bi-hourglass-split me-2"></i>
    Approval is <strong>pending</strong> — review in progress.
  </div>
  {{/is_pending}}

  {{#is_rejected}}
  <div class="alert alert-danger">
    <i class="bi bi-x-circle-fill me-2"></i>
    This supplier has been <strong>rejected</strong>.
  </div>
  {{/is_rejected}}

  <div class="page-number">Supplier {{_index}} of {{_total}}</div>
</div>
{{/rows}}`,

  image_basic: `<img src="/api/v1/images/IMAGE_ID/data" alt="Description" />`,

  image_header: `<div class="report-page">
  <div class="report-page-header d-flex align-items-center gap-3">
    <img src="/api/v1/images/IMAGE_ID/data"
         alt="Company Logo"
         style="height: 48px;" />
    <h1 class="mb-0">Monthly Report</h1>
  </div>

  <div class="report-page-content">
    <!-- report content here -->
  </div>
</div>`,

  image_styled: `<img src="/api/v1/images/IMAGE_ID/data"
     alt="Product photo"
     style="max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />`,

  chart3_template: `{{#rows}}
<div class="report-page">
  <div class="p-4">

    <!-- KPI tiles -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="report-tile tile-primary">
          <div class="report-tile-title">Team</div>
          <div class="report-tile-value">{{team_name}}</div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="report-tile tile-success">
          <div class="report-tile-title">Headcount</div>
          <div class="report-tile-value">{{headcount}}</div>
        </div>
      </div>
    </div>

    <!-- Chart driven by the struct array column -->
    <div class="chart-container">
      <div class="chart-title">Monthly Spend</div>
      <div class="report-bar-chart"
        data-labels="{{#spend_by_month}}{{month}},{{/spend_by_month}}"
        data-values="{{#spend_by_month}}{{spend}},{{/spend_by_month}}">
      </div>
    </div>

    <div class="page-number">Page {{_index}} of {{_total}}</div>
  </div>
</div>
{{/rows}}`,
}
</script>

<template>
  <div class="guide-view">
    <div class="guide-header mb-4">
      <h2 class="mb-1">
        <i class="bi bi-book text-primary me-2"></i>
        Template Guide
      </h2>
      <p class="text-muted mb-0">
        How to structure your data and write Mustache templates for reports
      </p>
    </div>

    <div class="row g-4">
      <!-- Nav -->
      <div class="col-md-3">
        <div class="card sticky-top" style="top: calc(var(--pr-navbar-height) + 1rem)">
          <div class="card-body p-2">
            <button
              v-for="s in sections"
              :key="s.id"
              class="guide-nav-btn"
              :class="{ active: activeSection === s.id }"
              @click="activeSection = s.id"
            >
              <i :class="['bi', s.icon, 'me-2']"></i>
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="col-md-9">

        <!-- ── Projects ── -->
        <div v-if="activeSection === 'projects'">
          <h4 class="section-title"><i class="bi bi-folder2-open me-2 text-primary"></i>Projects</h4>
          <p class="text-muted">Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p>

          <div class="card mb-4">
            <div class="card-header"><i class="bi bi-lightning me-2 text-warning"></i>Getting started</div>
            <div class="card-body">
              <ol class="mb-0">
                <li class="mb-2">Navigate to <strong>Projects</strong> and click <strong>New Project</strong>.</li>
                <li class="mb-2">Give it a name (e.g. "Q1 Sales Reports") and click <strong>Create</strong>.</li>
                <li class="mb-2">Click <strong>Open</strong> to set it as your active project — you'll see a banner in the sidebar.</li>
                <li class="mb-2">Now go to <strong>Data Structures</strong> — any structures you create will automatically belong to this project.</li>
                <li>Create templates linked to those structures and preview them as usual.</li>
              </ol>
            </div>
          </div>

          <div class="row g-4 mb-4">
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header"><i class="bi bi-diagram-3 me-2 text-primary"></i>How structures are linked</div>
                <div class="card-body">
                  <p class="small mb-2">When a project is active, new structures are automatically associated with it via a <code>project_id</code> field.</p>
                  <p class="small mb-2">The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p>
                  <p class="small mb-0 text-muted">Clear the project filter (click the <i class="bi bi-x-lg"></i> in the sidebar banner) to see all structures across all projects.</p>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header"><i class="bi bi-file-code me-2 text-success"></i>How templates are linked</div>
                <div class="card-body">
                  <p class="small mb-2">Templates don't have a direct project link — they're associated through their <strong>structure</strong>.</p>
                  <p class="small mb-0">When filtering by project, the app shows templates whose linked structure belongs to the active project.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="card mb-4">
            <div class="card-header"><i class="bi bi-lock me-2 text-warning"></i>Locking</div>
            <div class="card-body">
              <p class="small mb-2">Only the project <strong>owner</strong> can lock or unlock a project.</p>
              <p class="small mb-2">When a project is <strong>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code>423 Locked</code> response.</p>
              <p class="small mb-0 text-muted">This is useful when a report set is finalised and you want to prevent accidental edits.</p>
            </div>
          </div>

          <div class="card mb-4">
            <div class="card-header"><i class="bi bi-people me-2 text-info"></i>Sharing</div>
            <div class="card-body">
              <p class="small mb-2">Share a project with colleagues by entering their email address on the project detail panel.</p>
              <p class="small mb-2">Shared users can <strong>view</strong> and <strong>edit</strong> structures and templates in the project (unless it's locked).</p>
              <p class="small mb-2">Only the project <strong>owner</strong> can:</p>
              <ul class="small mb-0">
                <li>Lock / unlock the project</li>
                <li>Add or remove shares</li>
                <li>Delete the project</li>
              </ul>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><i class="bi bi-table me-2"></i>Permission summary</div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-dark">
                  <tr><th>Action</th><th>Owner</th><th>Shared user</th></tr>
                </thead>
                <tbody>
                  <tr><td>View structures &amp; templates</td><td class="text-success">Yes</td><td class="text-success">Yes</td></tr>
                  <tr><td>Create / edit / delete structures &amp; templates</td><td class="text-success">Yes (if unlocked)</td><td class="text-success">Yes (if unlocked)</td></tr>
                  <tr><td>Lock / unlock project</td><td class="text-success">Yes</td><td class="text-danger">No</td></tr>
                  <tr><td>Share / unshare project</td><td class="text-success">Yes</td><td class="text-danger">No</td></tr>
                  <tr><td>Delete project</td><td class="text-success">Yes</td><td class="text-danger">No</td></tr>
                  <tr><td>Rename project</td><td class="text-success">Yes</td><td class="text-danger">No</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ── Mustache Syntax ── -->
        <div v-if="activeSection === 'mustache'">
          <h4 class="section-title"><i class="bi bi-braces me-2 text-primary"></i>Mustache Syntax Reference</h4>
          <p class="text-muted">Mustache is a logic-less templating language. All data comes from the <code>rows</code> array returned by your SQL query.</p>

          <div class="card mb-4">
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-dark">
                  <tr><th>Syntax</th><th>Purpose</th><th>Example</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code class="syntax-tag">{{ t.variable }}</code></td>
                    <td>Render a value (HTML-escaped)</td>
                    <td><code>{{ t.ex_field }}</code></td>
                  </tr>
                  <tr>
                    <td><code class="syntax-tag">{{ t.triple }}</code></td>
                    <td>Render raw HTML (unescaped)</td>
                    <td><code>{{ t.triple }}</code></td>
                  </tr>
                  <tr>
                    <td><code class="syntax-tag">{{ t.section }}</code></td>
                    <td>Iterate array <strong>or</strong> render if truthy</td>
                    <td><code>{{ t.rows_open }}...{{ t.rows_close }}</code></td>
                  </tr>
                  <tr>
                    <td><code class="syntax-tag">{{ t.inverted }}</code></td>
                    <td>Render if falsy or empty</td>
                    <td><code>{{ t.delete_check }}</code></td>
                  </tr>
                  <tr>
                    <td><code class="syntax-tag">{{ t.dot }}</code></td>
                    <td>Current item in a <em>scalar</em> list only</td>
                    <td><code>{{ t.ex_dot_loop }}</code> (tags is <code>["a","b"]</code>)</td>
                  </tr>
                  <tr>
                    <td><code class="syntax-tag">{{ t.comment }}</code></td>
                    <td>Comment — not rendered</td>
                    <td><code>{{ t.ex_comment }}</code></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <strong>Closing tags must always match the opening name exactly.</strong>
            <code class="ms-1">{{ t.rows_open }}</code> closes with <code>{{ t.rows_close }}</code> — never <code>{{ t.rows_wrong }}</code>.
          </div>

          <div class="card">
            <div class="card-header"><i class="bi bi-lightbulb me-2 text-warning"></i>Key rule — your data is always <code>rows</code></div>
            <div class="card-body">
              <p class="mb-2">Every query returns a single top-level key <code>rows</code>, which is a list of objects:</p>
              <pre class="code-block">{{ code.dataShape }}</pre>
              <p class="mb-0 small text-muted mt-2">Each row also receives <code>{{ t.index }}</code> (1-based position) and <code>{{ t.total }}</code> (total row count) automatically.</p>
            </div>
          </div>
        </div>

        <!-- ── Flat Table ── -->
        <div v-if="activeSection === 'flat-table'">
          <h4 class="section-title"><i class="bi bi-table me-2 text-primary"></i>Flat Table Report</h4>
          <p class="text-muted">The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.</p>

          <div class="pattern-step">
            <div class="step-label">1 · Unity Catalog Table</div>
            <pre class="code-block">{{ code.flatTable_sql }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">2 · Data Shape delivered to template</div>
            <pre class="code-block">{{ code.flatTable_data }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">3 · Mustache Template</div>
            <pre class="code-block">{{ code.flatTable_template }}</pre>
          </div>

          <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>
            <strong>Null / empty check:</strong> use <code>{{ t.inverted }}</code> to render content when a field is null, false, or empty — no logic needed.
          </div>
        </div>

        <!-- ── Struct Fields ── -->
        <div v-if="activeSection === 'struct'">
          <h4 class="section-title"><i class="bi bi-braces-asterisk me-2 text-primary"></i>Struct Fields</h4>
          <p class="text-muted">When a column is <code>STRUCT&lt;...&gt;</code>, Mustache can push it as a context or access it with dot notation.</p>

          <div class="pattern-step">
            <div class="step-label">1 · Unity Catalog Table with a STRUCT column</div>
            <pre class="code-block">{{ code.struct_sql }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">2 · Data Shape</div>
            <pre class="code-block">{{ code.struct_data }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">3 · Template — two equivalent approaches</div>
            <div class="row g-3">
              <div class="col-md-6">
                <div class="approach-card">
                  <div class="approach-label">Context push (recommended)</div>
                  <pre class="code-block">{{ code.struct_context }}</pre>
                  <p class="small text-muted mt-2 mb-0"><code>{{ t.address_open }}</code> pushes the struct as context — child fields are then in scope directly.</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="approach-card">
                  <div class="approach-label">Dot notation</div>
                  <pre class="code-block">{{ code.struct_dot }}</pre>
                  <p class="small text-muted mt-2 mb-0">Dot notation accesses nested fields without a context push — useful for one or two fields.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Array of Structs ── -->
        <div v-if="activeSection === 'array-struct'">
          <h4 class="section-title"><i class="bi bi-list-nested me-2 text-primary"></i>Array of Structs</h4>
          <p class="text-muted">When a column is <code>ARRAY&lt;STRUCT&lt;...&gt;&gt;</code>, iterate the outer <code>rows</code> first, then the nested array inside.</p>

          <div class="pattern-step">
            <div class="step-label">1 · Unity Catalog Table with ARRAY&lt;STRUCT&gt;</div>
            <pre class="code-block">{{ code.array_sql }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">2 · Data Shape</div>
            <pre class="code-block">{{ code.array_data }}</pre>
          </div>

          <div class="pattern-step">
            <div class="step-label">3 · Template — nested iteration</div>
            <pre class="code-block">{{ code.array_template }}</pre>
          </div>

          <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>
            <strong>One page per order:</strong> the outer <code>{{ t.rows_open }}</code> wraps a <code>.report-page</code> div, so each order gets its own page. <code>{{ t.index }}</code> and <code>{{ t.total }}</code> are available on each row.
          </div>
        </div>

        <!-- ── Charts from Structs ── -->
        <div v-if="activeSection === 'chart-struct'">
          <h4 class="section-title"><i class="bi bi-bar-chart me-2 text-primary"></i>Charts from Struct Columns</h4>
          <p class="text-muted">Charts read comma-separated strings from <code>data-labels</code> and <code>data-values</code> attributes. There are three ways to feed data in.</p>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-1">Pattern 1 — Aggregate the main <code>rows</code> array (simplest)</div>
            <div class="card-body">
              <p class="small text-muted mb-3">Use when each row already represents one data point you want to plot.</p>
              <pre class="code-block">{{ code.chart1_template }}</pre>
              <p class="small text-muted mt-2 mb-0">Mustache renders the loops into: <code>data-labels="EMEA,APAC,AMER,"</code> — trailing commas are ignored by the parser.</p>
            </div>
          </div>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-2">Pattern 2 — Pre-aggregated scalar columns</div>
            <div class="card-body">
              <p class="small text-muted mb-3">SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.</p>
              <pre class="code-block">{{ code.chart2_template }}</pre>
            </div>
          </div>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-3">Pattern 3 — ARRAY&lt;STRUCT&gt; chart column (self-contained)</div>
            <div class="card-body">
              <p class="small text-muted mb-3">The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.</p>

              <div class="pattern-step">
                <div class="step-label">SQL</div>
                <pre class="code-block">{{ code.chart3_sql }}</pre>
              </div>
              <div class="pattern-step">
                <div class="step-label">Data Shape</div>
                <pre class="code-block">{{ code.chart3_data }}</pre>
              </div>
              <div class="pattern-step">
                <div class="step-label">Template — one page per team, each with its own chart</div>
                <pre class="code-block">{{ code.chart3_template }}</pre>
              </div>

              <div class="alert alert-success mb-0">
                <i class="bi bi-check-circle-fill me-2"></i>
                <strong>Why this pattern is powerful:</strong> each team's chart is driven entirely by its own <code>spend_by_month</code> array — no global aggregation needed in the template. The SQL does the work, the template just renders it.
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><i class="bi bi-table me-2"></i>Pattern comparison</div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-dark">
                  <tr><th>Pattern</th><th>SQL complexity</th><th>Best for</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="badge pattern-badge-1">1 — Aggregate rows</span></td>
                    <td>Low</td>
                    <td>Single summary chart across all rows</td>
                  </tr>
                  <tr>
                    <td><span class="badge pattern-badge-2">2 — Scalar columns</span></td>
                    <td>Low–Medium</td>
                    <td>Fixed labels, one summary row</td>
                  </tr>
                  <tr>
                    <td><span class="badge pattern-badge-3">3 — Struct array</span></td>
                    <td>Medium</td>
                    <td>Per-row charts with different datasets on each page</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ── Conditional Styles ── -->
        <div v-if="activeSection === 'conditional-styles'">
          <h4 class="section-title"><i class="bi bi-palette me-2 text-primary"></i>Conditional Styles</h4>
          <p class="text-muted">Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.</p>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-1">Pattern 1 — CSS class from value (styling only, no SQL changes)</div>
            <div class="card-body">
              <p class="small text-muted mb-3">
                Interpolate the field value directly into the class name.
                Add a <code>&lt;style&gt;</code> block at the top of your template with one rule per expected value.
                Best for badge colours, row highlights, or any purely visual difference.
              </p>

              <div class="pattern-step">
                <div class="step-label">SQL — no changes needed</div>
                <pre class="code-block">{{ code.conditional_sql_pattern1 }}</pre>
              </div>

              <div class="pattern-step">
                <div class="step-label">Template</div>
                <pre class="code-block">{{ code.conditional_template_pattern1 }}</pre>
              </div>

              <div class="alert alert-success mb-0">
                <i class="bi bi-check-circle-fill me-2"></i>
                <strong>How it works:</strong> <code>{{ t.cond_class_example }}</code> renders as <code>status-approved</code>, <code>status-pending</code>, or <code>status-rejected</code>.
                Your CSS rules match on those exact class names.
              </div>
            </div>
          </div>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-2">Pattern 2 — SQL boolean flags (show/hide entire blocks)</div>
            <div class="card-body">
              <p class="small text-muted mb-3">
                Add computed boolean columns to your SQL query. Mustache sections
                (<code>{{ t.section }}</code>) render only when the value is truthy, giving you
                a full conditional block — not just a style change.
              </p>

              <div class="pattern-step">
                <div class="step-label">SQL — add boolean columns</div>
                <pre class="code-block">{{ code.conditional_sql_pattern2 }}</pre>
              </div>

              <div class="pattern-step">
                <div class="step-label">Template — conditional blocks</div>
                <pre class="code-block">{{ code.conditional_template_pattern2 }}</pre>
              </div>

              <div class="alert alert-info mb-0">
                <i class="bi bi-info-circle me-2"></i>
                <strong>When to use Pattern 2:</strong> when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers.
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><i class="bi bi-table me-2"></i>Pattern comparison</div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-dark">
                  <tr><th>Pattern</th><th>SQL change?</th><th>Best for</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="badge pattern-badge-1">1 — CSS class from value</span></td>
                    <td>None</td>
                    <td>Badge colours, row highlights, status indicators</td>
                  </tr>
                  <tr>
                    <td><span class="badge pattern-badge-2">2 — SQL boolean flags</span></td>
                    <td>Add <code>field = 'value' AS is_x</code></td>
                    <td>Conditional blocks, different content per status</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ── Images ── -->
        <div v-if="activeSection === 'images'">
          <h4 class="section-title"><i class="bi bi-images me-2 text-primary"></i>Images in Templates</h4>
          <p class="text-muted">Upload images to the gallery and reference them in your report templates using standard HTML <code>&lt;img&gt;</code> tags.</p>

          <div class="card mb-4">
            <div class="card-header"><i class="bi bi-lightning me-2 text-warning"></i>Quick start</div>
            <div class="card-body">
              <ol class="mb-0">
                <li class="mb-2">Go to <strong>Image Gallery</strong> (make sure you have an active project).</li>
                <li class="mb-2">Upload an image — drag &amp; drop or click <strong>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li>
                <li class="mb-2">Click the <i class="bi bi-link-45deg"></i> button on the image card to copy its URL.</li>
                <li>Paste the URL into an <code>&lt;img&gt;</code> tag in your template.</li>
              </ol>
            </div>
          </div>

          <div class="pattern-card mb-4">
            <div class="pattern-header pattern-1">Using images in templates</div>
            <div class="card-body">
              <p class="small text-muted mb-3">Use the image URL directly in an <code>&lt;img&gt;</code> tag. You can also use just the path (without the domain) since the report renders on the same origin.</p>

              <div class="pattern-step">
                <div class="step-label">Basic image</div>
                <pre class="code-block">{{ code.image_basic }}</pre>
              </div>

              <div class="pattern-step">
                <div class="step-label">Logo in a report header</div>
                <pre class="code-block">{{ code.image_header }}</pre>
              </div>

              <div class="pattern-step">
                <div class="step-label">Sized and styled</div>
                <pre class="code-block">{{ code.image_styled }}</pre>
              </div>
            </div>
          </div>

          <div class="card mb-4">
            <div class="card-header"><i class="bi bi-exclamation-triangle me-2 text-warning"></i>Limitations</div>
            <div class="card-body">
              <table class="table table-sm mb-0">
                <thead class="table-dark">
                  <tr><th>Works</th><th>Does not work</th></tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code>&lt;img src="/api/v1/images/ID/data"&gt;</code></td>
                    <td><code>background-image: url(/api/v1/images/ID/data)</code></td>
                  </tr>
                  <tr>
                    <td>Standard <code>&lt;img&gt;</code> tags with inline styles</td>
                    <td>CSS <code>url()</code> references to gallery images (blocked by sanitizer)</td>
                  </tr>
                </tbody>
              </table>
              <p class="small text-muted mt-2 mb-0">
                The template CSS sanitizer strips non-<code>data:</code> URLs in stylesheets for security. Use <code>&lt;img&gt;</code> tags instead of CSS background images.
              </p>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><i class="bi bi-info-circle me-2 text-info"></i>Tips</div>
            <div class="card-body">
              <ul class="small mb-0">
                <li class="mb-2">Each project can hold up to <strong>20 images</strong>, each up to <strong>2 MB</strong>.</li>
                <li class="mb-2">Images are served with a 24-hour browser cache header, so they load quickly in previews.</li>
                <li class="mb-2">Use the <strong>Rename</strong> button to give images descriptive names for easy identification.</li>
                <li>For logos and icons, <strong>SVG</strong> or <strong>WebP</strong> formats give the best quality-to-size ratio.</li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.guide-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.section-title {
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--pr-dark);
}

/* Sidebar nav */
.guide-nav-btn {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.6rem 0.75rem;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #495057;
  margin-bottom: 0.15rem;
  transition: all 0.15s ease;
}
.guide-nav-btn:hover { background: #f0f4f8; }
.guide-nav-btn.active {
  background: var(--databricks-orange);
  color: white;
  font-weight: 600;
}

/* Steps */
.pattern-step { margin-bottom: 1.25rem; }
.step-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c757d;
  margin-bottom: 0.4rem;
}

/* Code blocks */
.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.78rem;
  line-height: 1.55;
  padding: 0.9rem 1rem;
  border-radius: 6px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
}

.syntax-tag {
  background: #1e1e1e;
  color: #ce9178;
  font-size: 0.78rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

/* Pattern cards */
.pattern-card {
  border: none;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
}
.pattern-header {
  padding: 0.6rem 1rem;
  font-weight: 600;
  font-size: 0.875rem;
}
.pattern-1 { background: #e3f2fd; color: #1565c0; }
.pattern-2 { background: #e8f5e9; color: #2e7d32; }
.pattern-3 { background: #fff3e0; color: #e65100; }

.pattern-badge-1 { background-color: #1565c0; }
.pattern-badge-2 { background-color: #2e7d32; }
.pattern-badge-3 { background-color: #e65100; }

/* Approach cards */
.approach-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 0.75rem;
}
.approach-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--databricks-orange);
  margin-bottom: 0.5rem;
  letter-spacing: 0.06em;
}
</style>
