import{d as m,c as r,a as t,b as e,F as u,v as f,e as i,y as n,x as s,D as g,o as b,w as v,_ as h}from"./index-13ztZvN7.js";const y={class:"guide-view"},w={class:"row g-4"},k={class:"col-md-3"},_={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},x={class:"card-body p-2"},S=["onClick"],T={class:"col-md-9"},C={key:0},A={key:1},R={class:"card mb-4"},M={class:"card-body p-0"},q={class:"table table-sm mb-0"},P={class:"syntax-tag"},E={class:"syntax-tag"},j={class:"syntax-tag"},L={class:"syntax-tag"},I={class:"syntax-tag"},D={class:"syntax-tag"},U={class:"alert alert-warning"},F={class:"ms-1"},H={class:"card"},N={class:"card-body"},O={class:"code-block"},G={class:"mb-0 small text-muted mt-2"},V={key:2},Q={class:"pattern-step"},W={class:"code-block"},Y={class:"pattern-step"},B={class:"code-block"},K={class:"pattern-step"},z={class:"code-block"},J={class:"alert alert-info"},$={key:3},X={class:"pattern-step"},Z={class:"code-block"},tt={class:"pattern-step"},at={class:"code-block"},et={class:"pattern-step"},st={class:"row g-3"},dt={class:"col-md-6"},lt={class:"approach-card"},ot={class:"code-block"},rt={class:"small text-muted mt-2 mb-0"},it={class:"col-md-6"},bt={class:"approach-card"},nt={class:"code-block"},ct={key:4},vt={class:"pattern-step"},pt={class:"code-block"},mt={class:"pattern-step"},ut={class:"code-block"},ft={class:"pattern-step"},gt={class:"code-block"},ht={class:"alert alert-info"},yt={key:5},wt={class:"pattern-card mb-4"},kt={class:"card-body"},_t={class:"code-block"},xt={class:"pattern-card mb-4"},St={class:"card-body"},Tt={class:"code-block"},Ct={class:"pattern-card mb-4"},At={class:"card-body"},Rt={class:"pattern-step"},Mt={class:"code-block"},qt={class:"pattern-step"},Pt={class:"code-block"},Et={class:"pattern-step"},jt={class:"code-block"},Lt={class:"card mb-4"},It={class:"card-body"},Dt={class:"code-block"},Ut={class:"card"},Ft={class:"card-body"},Ht={class:"code-block"},Nt={key:6},Ot={class:"pattern-card mb-4"},Gt={class:"card-body"},Vt={class:"pattern-step"},Qt={class:"code-block"},Wt={class:"pattern-step"},Yt={class:"code-block"},Bt={class:"alert alert-success mb-0"},Kt={class:"pattern-card mb-4"},zt={class:"card-body"},Jt={class:"small text-muted mb-3"},$t={class:"pattern-step"},Xt={class:"code-block"},Zt={class:"pattern-step"},ta={class:"code-block"},aa={key:7},ea={class:"pattern-card mb-4"},sa={class:"card-body"},da={class:"pattern-step"},la={class:"code-block"},oa={class:"pattern-step"},ra={class:"code-block"},ia={class:"pattern-step"},ba={class:"code-block"},na={key:8},ca={class:"card mb-4"},va={class:"card-body"},pa={class:"small text-muted mb-3"},ma={class:"code-block"},ua={class:"card mb-4"},fa={class:"card-body"},ga={class:"small text-muted mb-3"},ha={class:"code-block"},ya={class:"card mb-4"},wa={class:"card-body"},ka={class:"code-block"},_a={key:9},xa={key:10},Sa={class:"card mb-4"},Ta={class:"card-body"},Ca={class:"code-block"},Aa={class:"card mb-4"},Ra={class:"card-body"},Ma={class:"code-block"},qa={class:"card mb-4"},Pa={class:"card-body"},Ea={class:"code-block"},ja={class:"code-block"},La={class:"card mb-4"},Ia={class:"card-body"},Da={class:"code-block"},Ua={class:"card mb-4"},Fa={class:"card-body"},Ha={class:"code-block"},Na=m({__name:"GuideView",setup(Oa){const o=g("projects"),p=[{id:"projects",label:"Projects",icon:"bi-folder2-open"},{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"},{id:"images",label:"Images",icon:"bi-images"},{id:"markdown",label:"Markdown Templates",icon:"bi-markdown"},{id:"scheduling",label:"Scheduling",icon:"bi-clock-history"},{id:"pagination",label:"Pagination Magic",icon:"bi-layout-text-sidebar-reverse"}],l={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},d={dataShape:`{
  "rows": [
    { "field1": "value", "field2": 42 },
    { "field1": "value", "field2": 99 }
  ]
}`,flatTable_sql:`-- system.compute.clusters (example)
cluster_name   VARCHAR
cluster_id     VARCHAR
owned_by       VARCHAR
worker_count   INT
create_time    TIMESTAMP
delete_time    TIMESTAMP   -- NULL if still active`,flatTable_data:`{
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
}`,flatTable_template:`<div class="report-page">
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
</div>`,struct_sql:`-- employee table
name          VARCHAR
department    VARCHAR
address       STRUCT<
                city:    VARCHAR,
                country: VARCHAR,
                zip:     VARCHAR
              >`,struct_data:`{
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
}`,struct_context:`{{#rows}}
  <td>{{name}}</td>

  {{#address}}
    <td>{{city}}</td>
    <td>{{country}}</td>
    <td>{{zip}}</td>
  {{/address}}
{{/rows}}`,struct_dot:`{{#rows}}
  <td>{{name}}</td>
  <td>{{address.city}}</td>
  <td>{{address.country}}</td>
  <td>{{address.zip}}</td>
{{/rows}}`,array_sql:`-- order table
order_id      VARCHAR
customer      VARCHAR
items         ARRAY<STRUCT<
                product: VARCHAR,
                qty:     INT,
                price:   DOUBLE
              >>`,array_data:`{
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
}`,array_template:`{{#rows}}
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
{{/rows}}`,chart1_template:`<!-- SQL: SELECT region, SUM(revenue) as total FROM sales GROUP BY region -->

<div class="chart-container">
  <div class="chart-title">Revenue by Region</div>
  <div class="report-bar-chart"
    data-labels="{{#rows}}{{region}},{{/rows}}"
    data-values="{{#rows}}{{total}},{{/rows}}">
  </div>
</div>`,chart2_template:`<!-- SQL: SELECT active_count, terminated_count FROM cluster_summary -->

<div class="chart-container">
  <div class="chart-title">Cluster Status</div>
  <div class="report-pie-chart"
    data-labels="Active,Terminated"
    data-values="{{#rows}}{{active_count}},{{terminated_count}}{{/rows}}">
  </div>
</div>`,chart3_sql:`SELECT
  team_name,
  headcount,
  -- pre-aggregate monthly spend into an array
  array_agg(
    named_struct('month', month_name, 'spend', monthly_spend)
    ORDER BY month_num
  ) AS spend_by_month
FROM team_metrics
GROUP BY team_name, headcount`,chart3_data:`{
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
}`,conditional_sql_pattern1:`-- No changes needed — use the field value directly as a CSS class
SELECT
  supplier_name,
  approval_status,   -- e.g. 'approved', 'pending', 'rejected'
  category,
  onboarded_date
FROM procurement.suppliers`,conditional_template_pattern1:`<style>
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
{{/rows}}`,conditional_sql_pattern2:`-- Add boolean columns in SQL for full block conditionals
SELECT
  supplier_name,
  approval_status,
  category,
  onboarded_date,
  approval_status = 'approved' AS is_approved,
  approval_status = 'pending'  AS is_pending,
  approval_status = 'rejected' AS is_rejected
FROM procurement.suppliers`,conditional_template_pattern2:`{{#rows}}
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
{{/rows}}`,markdown_basic:`# {{title}}

Generated: {{date}}

> **Total rows:** {{_total}}

---

{{#rows}}
## {{name}}

| Field | Value |
|-------|-------|
| Status | {{status}} |
| Amount | {{amount}} |

<div class="page-break"></div>
{{/rows}}`,markdown_table:`| Name | Department | Status |
|------|-----------|--------|
{{#rows}}| {{name}} | {{department}} | {{status}} |
{{/rows}}`,image_basic:'<img src="img:IMAGE_ID" alt="Description" />',pagination_break_after:`<!-- Force page break AFTER this point -->
<div class="page-break"></div>

<!-- Force page break BEFORE the next content block -->
<div class="page-break-before"></div>`,pagination_no_break:`<!-- Keep this block together — don't split across pages -->
<div class="no-break">
  <h2>Section Heading</h2>
  <p>Opening paragraph that should stay with the heading.</p>
  <div class="report-tile tile-primary">
    <div class="report-tile-title">KPI</div>
    <div class="report-tile-value">{{value}}</div>
  </div>
</div>`,pagination_break_after_n:`<!-- Auto page break every 20 rows — no need to count manually -->
<div data-break-after="20">
  {{#rows}}
  <div class="d-flex justify-content-between border-bottom py-2">
    <span>{{name}}</span>
    <span class="fw-semibold">{{amount}}</span>
  </div>
  {{/rows}}
</div>`,pagination_break_after_table:`<table class="report-table">
  <thead>
    <tr><th>Name</th><th>Department</th><th>Status</th></tr>
  </thead>
  <tbody>
    <div data-break-after="25">
      {{#rows}}<tr>
        <td>{{name}}</td>
        <td>{{department}}</td>
        <td>{{status}}</td>
      </tr>{{/rows}}
    </div>
  </tbody>
</table>`,pagination_global_header:`<!-- Define ONCE — automatically cloned into every .report-page -->
<div class="report-global-header">
  <div class="d-flex justify-content-between align-items-center">
    <img src="img:LOGO_ID" alt="Logo" style="height: 36px;" />
    <span class="text-muted small fw-semibold">Monthly Revenue Report</span>
  </div>
</div>

<div class="report-global-footer">
  <div class="d-flex justify-content-between small text-muted">
    <span>Confidential — Internal Use Only</span>
    <span>Page {{_index}} of {{_total}}</span>
  </div>
</div>

<div class="report-page">
  <!-- Header and footer appear here automatically -->
  <h1>January Summary</h1>
  ...
</div>
<div class="report-page">
  <!-- Header and footer appear here automatically too -->
  <h1>February Summary</h1>
  ...
</div>`,pagination_columns:`<!-- 2-column layout -->
<div class="report-columns-2">
  {{#rows}}
  <div class="mb-3">
    <div class="fw-semibold">{{name}}</div>
    <div class="text-muted small">{{region}} · {{status}}</div>
  </div>
  {{/rows}}
</div>

<!-- 3-column layout (great for compact KPI grids) -->
<div class="report-columns-3">
  {{#rows}}
  <div class="report-tile tile-primary mb-3">
    <div class="report-tile-title">{{category}}</div>
    <div class="report-tile-value">{{total}}</div>
  </div>
  {{/rows}}
</div>`,image_header:`<div class="report-page">
  <div class="report-page-header d-flex align-items-center gap-3">
    <img src="img:IMAGE_ID"
         alt="Company Logo"
         style="height: 48px;" />
    <h1 class="mb-0">Monthly Report</h1>
  </div>

  <div class="report-page-content">
    <!-- report content here -->
  </div>
</div>`,image_styled:`<img src="img:IMAGE_ID"
     alt="Product photo"
     style="max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />`,chart3_template:`{{#rows}}
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
{{/rows}}`,chart_opts_bar:`<div class="report-bar-chart"
  data-labels="{{#rows}}{{region}},{{/rows}}"
  data-values="{{#rows}}{{total}},{{/rows}}"
  data-title="Revenue by Region"
  data-color-scheme="blues"
  data-y-title="Revenue ($)"
  data-sort="descending">
</div>`,chart_opts_donut:`<div class="report-pie-chart"
  data-labels="{{#rows}}{{category}},{{/rows}}"
  data-values="{{#rows}}{{amount}},{{/rows}}"
  data-title="Spend by Category"
  data-inner-radius="50">
</div>`,markdown_chart:`## Revenue Summary

{{#rows}}
**{{region}}**: \${{total}}
{{/rows}}

<div class="report-bar-chart"
  data-labels="{{#rows}}{{region}},{{/rows}}"
  data-values="{{#rows}}{{total}},{{/rows}}"
  data-title="Revenue by Region"
  data-color-scheme="blues">
</div>`};return(Ga,a)=>(b(),r("div",y,[a[136]||(a[136]=t("div",{class:"guide-header mb-4"},[t("h2",{class:"mb-1"},[t("i",{class:"bi bi-book text-primary me-2"}),e(" Template Guide ")]),t("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),t("div",w,[t("div",k,[t("div",_,[t("div",x,[(b(),r(u,null,f(p,c=>t("button",{key:c.id,class:v(["guide-nav-btn",{active:o.value===c.id}]),onClick:Va=>o.value=c.id},[t("i",{class:v(["bi",c.icon,"me-2"])},null,2),e(" "+s(c.label),1)],10,S)),64))])])]),t("div",T,[o.value==="projects"?(b(),r("div",C,[...a[0]||(a[0]=[i('<h4 class="section-title" data-v-7fb71b32><i class="bi bi-folder2-open me-2 text-primary" data-v-7fb71b32></i>Projects</h4><p class="text-muted" data-v-7fb71b32>Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-lightning me-2 text-warning" data-v-7fb71b32></i>Getting started</div><div class="card-body" data-v-7fb71b32><ol class="mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Navigate to <strong data-v-7fb71b32>Projects</strong> and click <strong data-v-7fb71b32>New Project</strong>.</li><li class="mb-2" data-v-7fb71b32>Give it a name (e.g. &quot;Q1 Sales Reports&quot;) and click <strong data-v-7fb71b32>Create</strong>.</li><li class="mb-2" data-v-7fb71b32>Click <strong data-v-7fb71b32>Open</strong> to set it as your active project — you&#39;ll see a banner in the sidebar.</li><li class="mb-2" data-v-7fb71b32>Now go to <strong data-v-7fb71b32>Data Structures</strong> — any structures you create will automatically belong to this project.</li><li data-v-7fb71b32>Create templates linked to those structures, then use the <strong data-v-7fb71b32>Export</strong> button in the Template Editor to preview with real data (configurable row count) and export to PDF.</li></ol></div></div><div class="row g-4 mb-4" data-v-7fb71b32><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-diagram-3 me-2 text-primary" data-v-7fb71b32></i>How structures are linked</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>When a project is active, new structures are automatically associated with it via a <code data-v-7fb71b32>project_id</code> field.</p><p class="small mb-2" data-v-7fb71b32>The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p><p class="small mb-0 text-muted" data-v-7fb71b32>Clear the project filter (click the <i class="bi bi-x-lg" data-v-7fb71b32></i> in the sidebar banner) to see all structures across all projects.</p></div></div></div><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-file-code me-2 text-success" data-v-7fb71b32></i>How templates are linked</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>Templates don&#39;t have a direct project link — they&#39;re associated through their <strong data-v-7fb71b32>structure</strong>.</p><p class="small mb-0" data-v-7fb71b32>When filtering by project, the app shows templates whose linked structure belongs to the active project.</p></div></div></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-lock me-2 text-warning" data-v-7fb71b32></i>Locking</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>Only the project <strong data-v-7fb71b32>owner</strong> can lock or unlock a project.</p><p class="small mb-2" data-v-7fb71b32>When a project is <strong data-v-7fb71b32>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code data-v-7fb71b32>423 Locked</code> response.</p><p class="small mb-0 text-muted" data-v-7fb71b32>This is useful when a report set is finalised and you want to prevent accidental edits.</p></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-people me-2 text-info" data-v-7fb71b32></i>Sharing</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>Share a project with colleagues by entering their email address on the project detail panel.</p><p class="small mb-2" data-v-7fb71b32>Shared users can <strong data-v-7fb71b32>view</strong> and <strong data-v-7fb71b32>edit</strong> structures and templates in the project (unless it&#39;s locked).</p><p class="small mb-2" data-v-7fb71b32>Only the project <strong data-v-7fb71b32>owner</strong> can:</p><ul class="small mb-0" data-v-7fb71b32><li data-v-7fb71b32>Lock / unlock the project</li><li data-v-7fb71b32>Add or remove shares</li><li data-v-7fb71b32>Delete the project</li></ul></div></div><div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-table me-2" data-v-7fb71b32></i>Permission summary</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Action</th><th data-v-7fb71b32>Owner</th><th data-v-7fb71b32>Shared user</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32>View structures &amp; templates</td><td class="text-success" data-v-7fb71b32>Yes</td><td class="text-success" data-v-7fb71b32>Yes</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Create / edit / delete structures &amp; templates</td><td class="text-success" data-v-7fb71b32>Yes (if unlocked)</td><td class="text-success" data-v-7fb71b32>Yes (if unlocked)</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Lock / unlock project</td><td class="text-success" data-v-7fb71b32>Yes</td><td class="text-danger" data-v-7fb71b32>No</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Share / unshare project</td><td class="text-success" data-v-7fb71b32>Yes</td><td class="text-danger" data-v-7fb71b32>No</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Delete project</td><td class="text-success" data-v-7fb71b32>Yes</td><td class="text-danger" data-v-7fb71b32>No</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Rename project</td><td class="text-success" data-v-7fb71b32>Yes</td><td class="text-danger" data-v-7fb71b32>No</td></tr></tbody></table></div></div>',7)])])):n("",!0),o.value==="mustache"?(b(),r("div",A,[a[21]||(a[21]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces me-2 text-primary"}),e("Mustache Syntax Reference")],-1)),a[22]||(a[22]=t("p",{class:"text-muted"},[e("Mustache is a logic-less templating language. All data comes from the "),t("code",null,"rows"),e(" array returned by your SQL query.")],-1)),t("div",R,[t("div",M,[t("table",q,[a[10]||(a[10]=t("thead",{class:"table-dark"},[t("tr",null,[t("th",null,"Syntax"),t("th",null,"Purpose"),t("th",null,"Example")])],-1)),t("tbody",null,[t("tr",null,[t("td",null,[t("code",P,s(l.variable),1)]),a[1]||(a[1]=t("td",null,"Render a value (HTML-escaped)",-1)),t("td",null,[t("code",null,s(l.ex_field),1)])]),t("tr",null,[t("td",null,[t("code",E,s(l.triple),1)]),a[2]||(a[2]=t("td",null,"Render raw HTML (unescaped)",-1)),t("td",null,[t("code",null,s(l.triple),1)])]),t("tr",null,[t("td",null,[t("code",j,s(l.section),1)]),a[3]||(a[3]=t("td",null,[e("Iterate array "),t("strong",null,"or"),e(" render if truthy")],-1)),t("td",null,[t("code",null,s(l.rows_open)+"..."+s(l.rows_close),1)])]),t("tr",null,[t("td",null,[t("code",L,s(l.inverted),1)]),a[4]||(a[4]=t("td",null,"Render if falsy or empty",-1)),t("td",null,[t("code",null,s(l.delete_check),1)])]),t("tr",null,[t("td",null,[t("code",I,s(l.dot),1)]),a[8]||(a[8]=t("td",null,[e("Current item in a "),t("em",null,"scalar"),e(" list only")],-1)),t("td",null,[t("code",null,s(l.ex_dot_loop),1),a[5]||(a[5]=e(" (tags is ",-1)),a[6]||(a[6]=t("code",null,'["a","b"]',-1)),a[7]||(a[7]=e(")",-1))])]),t("tr",null,[t("td",null,[t("code",D,s(l.comment),1)]),a[9]||(a[9]=t("td",null,"Comment — not rendered",-1)),t("td",null,[t("code",null,s(l.ex_comment),1)])])])])])]),t("div",U,[a[11]||(a[11]=t("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),a[12]||(a[12]=t("strong",null,"Closing tags must always match the opening name exactly.",-1)),t("code",F,s(l.rows_open),1),a[13]||(a[13]=e(" closes with ",-1)),t("code",null,s(l.rows_close),1),a[14]||(a[14]=e(" — never ",-1)),t("code",null,s(l.rows_wrong),1),a[15]||(a[15]=e(". ",-1))]),t("div",H,[a[20]||(a[20]=t("div",{class:"card-header"},[t("i",{class:"bi bi-lightbulb me-2 text-warning"}),e("Key rule — your data is always "),t("code",null,"rows")],-1)),t("div",N,[a[19]||(a[19]=t("p",{class:"mb-2"},[e("Every query returns a single top-level key "),t("code",null,"rows"),e(", which is a list of objects:")],-1)),t("pre",O,s(d.dataShape),1),t("p",G,[a[16]||(a[16]=e("Each row also receives ",-1)),t("code",null,s(l.index),1),a[17]||(a[17]=e(" (1-based position) and ",-1)),t("code",null,s(l.total),1),a[18]||(a[18]=e(" (total row count) automatically.",-1))])])])])):n("",!0),o.value==="flat-table"?(b(),r("div",V,[a[30]||(a[30]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-table me-2 text-primary"}),e("Flat Table Report")],-1)),a[31]||(a[31]=t("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),t("div",Q,[a[23]||(a[23]=t("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),t("pre",W,s(d.flatTable_sql),1)]),t("div",Y,[a[24]||(a[24]=t("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),t("pre",B,s(d.flatTable_data),1)]),t("div",K,[a[25]||(a[25]=t("div",{class:"step-label"},"3 · Mustache Template",-1)),t("pre",z,s(d.flatTable_template),1)]),t("div",J,[a[26]||(a[26]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),a[27]||(a[27]=t("strong",null,"Null / empty check:",-1)),a[28]||(a[28]=e(" use ",-1)),t("code",null,s(l.inverted),1),a[29]||(a[29]=e(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),o.value==="struct"?(b(),r("div",$,[a[39]||(a[39]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),e("Struct Fields")],-1)),a[40]||(a[40]=t("p",{class:"text-muted"},[e("When a column is "),t("code",null,"STRUCT<...>"),e(", Mustache can push it as a context or access it with dot notation.")],-1)),t("div",X,[a[32]||(a[32]=t("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),t("pre",Z,s(d.struct_sql),1)]),t("div",tt,[a[33]||(a[33]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",at,s(d.struct_data),1)]),t("div",et,[a[38]||(a[38]=t("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),t("div",st,[t("div",dt,[t("div",lt,[a[35]||(a[35]=t("div",{class:"approach-label"},"Context push (recommended)",-1)),t("pre",ot,s(d.struct_context),1),t("p",rt,[t("code",null,s(l.address_open),1),a[34]||(a[34]=e(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),t("div",it,[t("div",bt,[a[36]||(a[36]=t("div",{class:"approach-label"},"Dot notation",-1)),t("pre",nt,s(d.struct_dot),1),a[37]||(a[37]=t("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),o.value==="array-struct"?(b(),r("div",ct,[a[52]||(a[52]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-list-nested me-2 text-primary"}),e("Array of Structs")],-1)),a[53]||(a[53]=t("p",{class:"text-muted"},[e("When a column is "),t("code",null,"ARRAY<STRUCT<...>>"),e(", iterate the outer "),t("code",null,"rows"),e(" first, then the nested array inside.")],-1)),t("div",vt,[a[41]||(a[41]=t("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),t("pre",pt,s(d.array_sql),1)]),t("div",mt,[a[42]||(a[42]=t("div",{class:"step-label"},"2 · Data Shape",-1)),t("pre",ut,s(d.array_data),1)]),t("div",ft,[a[43]||(a[43]=t("div",{class:"step-label"},"3 · Template — nested iteration",-1)),t("pre",gt,s(d.array_template),1)]),t("div",ht,[a[44]||(a[44]=t("i",{class:"bi bi-info-circle me-2"},null,-1)),a[45]||(a[45]=t("strong",null,"One page per order:",-1)),a[46]||(a[46]=e(" the outer ",-1)),t("code",null,s(l.rows_open),1),a[47]||(a[47]=e(" wraps a ",-1)),a[48]||(a[48]=t("code",null,".report-page",-1)),a[49]||(a[49]=e(" div, so each order gets its own page. ",-1)),t("code",null,s(l.index),1),a[50]||(a[50]=e(" and ",-1)),t("code",null,s(l.total),1),a[51]||(a[51]=e(" are available on each row. ",-1))])])):n("",!0),o.value==="chart-struct"?(b(),r("div",yt,[a[68]||(a[68]=i('<h4 class="section-title" data-v-7fb71b32><i class="bi bi-bar-chart me-2 text-primary" data-v-7fb71b32></i>Charts from Struct Columns</h4><div class="alert alert-success py-2 mb-3" data-v-7fb71b32><i class="bi bi-check-circle me-2" data-v-7fb71b32></i>Charts render as <strong data-v-7fb71b32>inline SVG</strong> — they display identically in the browser preview, PDF export, and email delivery. No JavaScript required at render time. </div><p class="text-muted" data-v-7fb71b32>Charts read comma-separated strings from <code data-v-7fb71b32>data-labels</code> and <code data-v-7fb71b32>data-values</code> attributes. There are three ways to feed data in.</p>',3)),t("div",wt,[a[56]||(a[56]=t("div",{class:"pattern-header pattern-1"},[e("Pattern 1 — Aggregate the main "),t("code",null,"rows"),e(" array (simplest)")],-1)),t("div",kt,[a[54]||(a[54]=t("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),t("pre",_t,s(d.chart1_template),1),a[55]||(a[55]=t("p",{class:"small text-muted mt-2 mb-0"},[e("Mustache renders the loops into: "),t("code",null,'data-labels="EMEA,APAC,AMER,"'),e(" — trailing commas are ignored by the parser.")],-1))])]),t("div",xt,[a[58]||(a[58]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),t("div",St,[a[57]||(a[57]=t("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),t("pre",Tt,s(d.chart2_template),1)])]),t("div",Ct,[a[64]||(a[64]=t("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),t("div",At,[a[62]||(a[62]=t("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),t("div",Rt,[a[59]||(a[59]=t("div",{class:"step-label"},"SQL",-1)),t("pre",Mt,s(d.chart3_sql),1)]),t("div",qt,[a[60]||(a[60]=t("div",{class:"step-label"},"Data Shape",-1)),t("pre",Pt,s(d.chart3_data),1)]),t("div",Et,[a[61]||(a[61]=t("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),t("pre",jt,s(d.chart3_template),1)]),a[63]||(a[63]=t("div",{class:"alert alert-success mb-0"},[t("i",{class:"bi bi-check-circle-fill me-2"}),t("strong",null,"Why this pattern is powerful:"),e(" each team's chart is driven entirely by its own "),t("code",null,"spend_by_month"),e(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),a[69]||(a[69]=i('<div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-table me-2" data-v-7fb71b32></i>Pattern comparison</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Pattern</th><th data-v-7fb71b32>SQL complexity</th><th data-v-7fb71b32>Best for</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge pattern-badge-1" data-v-7fb71b32>1 — Aggregate rows</span></td><td data-v-7fb71b32>Low</td><td data-v-7fb71b32>Single summary chart across all rows</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge pattern-badge-2" data-v-7fb71b32>2 — Scalar columns</span></td><td data-v-7fb71b32>Low–Medium</td><td data-v-7fb71b32>Fixed labels, one summary row</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge pattern-badge-3" data-v-7fb71b32>3 — Struct array</span></td><td data-v-7fb71b32>Medium</td><td data-v-7fb71b32>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-sliders me-2" data-v-7fb71b32></i>Optional chart attributes</div><div class="card-body" data-v-7fb71b32><p class="small text-muted mb-3" data-v-7fb71b32>All attributes are optional — existing chart divs work unchanged. Add them to customise appearance and behaviour without any template restructuring.</p><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Attribute</th><th data-v-7fb71b32>Applies to</th><th data-v-7fb71b32>Description</th><th data-v-7fb71b32>Example</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-title</code></td><td data-v-7fb71b32>bar, pie</td><td data-v-7fb71b32>Chart title rendered above the chart</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;Revenue by Region&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-color-scheme</code></td><td data-v-7fb71b32>bar, pie</td><td data-v-7fb71b32>Vega colour scheme name</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;blues&quot;</code>, <code data-v-7fb71b32>&quot;tableau10&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-width</code></td><td data-v-7fb71b32>bar, pie</td><td data-v-7fb71b32>Width in px (default: 500 bar / 300 pie)</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;400&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-height</code></td><td data-v-7fb71b32>bar, pie</td><td data-v-7fb71b32>Height in px (default: 250 bar / 300 pie)</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;200&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-x-title</code></td><td data-v-7fb71b32>bar</td><td data-v-7fb71b32>X-axis label</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;Quarter&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-y-title</code></td><td data-v-7fb71b32>bar</td><td data-v-7fb71b32>Y-axis label</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;Revenue ($)&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-sort</code></td><td data-v-7fb71b32>bar</td><td data-v-7fb71b32>Sort bars: <code data-v-7fb71b32>ascending</code>, <code data-v-7fb71b32>descending</code></td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;descending&quot;</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-inner-radius</code></td><td data-v-7fb71b32>pie</td><td data-v-7fb71b32>Inner radius in px — <code data-v-7fb71b32>0</code> = pie (default), <code data-v-7fb71b32>&gt;0</code> = donut</td><td data-v-7fb71b32><code data-v-7fb71b32>&quot;50&quot;</code></td></tr></tbody></table></div></div>',2)),t("div",Lt,[a[65]||(a[65]=t("div",{class:"card-header"},[t("i",{class:"bi bi-bar-chart me-2"}),e("Example: titled bar chart with colour scheme")],-1)),t("div",It,[t("pre",Dt,s(d.chart_opts_bar),1)])]),t("div",Ut,[a[67]||(a[67]=t("div",{class:"card-header"},[t("i",{class:"bi bi-pie-chart me-2"}),e("Example: donut chart")],-1)),t("div",Ft,[a[66]||(a[66]=t("p",{class:"small text-muted mb-3"},[e("Set "),t("code",null,"data-inner-radius"),e(" to any positive value to turn a pie chart into a donut. A value of "),t("code",null,"50"),e(" is a good starting point.")],-1)),t("pre",Ht,s(d.chart_opts_donut),1)])])])):n("",!0),o.value==="conditional-styles"?(b(),r("div",Nt,[a[90]||(a[90]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-palette me-2 text-primary"}),e("Conditional Styles")],-1)),a[91]||(a[91]=t("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),t("div",Ot,[a[83]||(a[83]=t("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),t("div",Gt,[a[82]||(a[82]=t("p",{class:"small text-muted mb-3"},[e(" Interpolate the field value directly into the class name. Add a "),t("code",null,"<style>"),e(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),t("div",Vt,[a[70]||(a[70]=t("div",{class:"step-label"},"SQL — no changes needed",-1)),t("pre",Qt,s(d.conditional_sql_pattern1),1)]),t("div",Wt,[a[71]||(a[71]=t("div",{class:"step-label"},"Template",-1)),t("pre",Yt,s(d.conditional_template_pattern1),1)]),t("div",Bt,[a[72]||(a[72]=t("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),a[73]||(a[73]=t("strong",null,"How it works:",-1)),a[74]||(a[74]=e()),t("code",null,s(l.cond_class_example),1),a[75]||(a[75]=e(" renders as ",-1)),a[76]||(a[76]=t("code",null,"status-approved",-1)),a[77]||(a[77]=e(", ",-1)),a[78]||(a[78]=t("code",null,"status-pending",-1)),a[79]||(a[79]=e(", or ",-1)),a[80]||(a[80]=t("code",null,"status-rejected",-1)),a[81]||(a[81]=e(". Your CSS rules match on those exact class names. ",-1))])])]),t("div",Kt,[a[89]||(a[89]=t("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),t("div",zt,[t("p",Jt,[a[84]||(a[84]=e(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),t("code",null,s(l.section),1),a[85]||(a[85]=e(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),t("div",$t,[a[86]||(a[86]=t("div",{class:"step-label"},"SQL — add boolean columns",-1)),t("pre",Xt,s(d.conditional_sql_pattern2),1)]),t("div",Zt,[a[87]||(a[87]=t("div",{class:"step-label"},"Template — conditional blocks",-1)),t("pre",ta,s(d.conditional_template_pattern2),1)]),a[88]||(a[88]=t("div",{class:"alert alert-info mb-0"},[t("i",{class:"bi bi-info-circle me-2"}),t("strong",null,"When to use Pattern 2:"),e(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),a[92]||(a[92]=i('<div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-table me-2" data-v-7fb71b32></i>Pattern comparison</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Pattern</th><th data-v-7fb71b32>SQL change?</th><th data-v-7fb71b32>Best for</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge pattern-badge-1" data-v-7fb71b32>1 — CSS class from value</span></td><td data-v-7fb71b32>None</td><td data-v-7fb71b32>Badge colours, row highlights, status indicators</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge pattern-badge-2" data-v-7fb71b32>2 — SQL boolean flags</span></td><td data-v-7fb71b32>Add <code data-v-7fb71b32>field = &#39;value&#39; AS is_x</code></td><td data-v-7fb71b32>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0),o.value==="images"?(b(),r("div",aa,[a[98]||(a[98]=i('<h4 class="section-title" data-v-7fb71b32><i class="bi bi-images me-2 text-primary" data-v-7fb71b32></i>Images in Templates</h4><p class="text-muted" data-v-7fb71b32>Upload images to the gallery and reference them in your report templates using standard HTML <code data-v-7fb71b32>&lt;img&gt;</code> tags.</p><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-lightning me-2 text-warning" data-v-7fb71b32></i>Quick start</div><div class="card-body" data-v-7fb71b32><ol class="mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Go to <strong data-v-7fb71b32>Image Gallery</strong> (make sure you have an active project).</li><li class="mb-2" data-v-7fb71b32>Upload an image — drag &amp; drop or click <strong data-v-7fb71b32>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li><li class="mb-2" data-v-7fb71b32>Click the <i class="bi bi-link-45deg" data-v-7fb71b32></i> button on the image card to copy its <code data-v-7fb71b32>img:UUID</code> reference.</li><li data-v-7fb71b32>Paste it into an <code data-v-7fb71b32>&lt;img&gt;</code> tag in your template: <code data-v-7fb71b32>&lt;img src=&quot;img:IMAGE_ID&quot; alt=&quot;…&quot; /&gt;</code></li></ol></div></div>',3)),t("div",ea,[a[97]||(a[97]=t("div",{class:"pattern-header pattern-1"},"Using images in templates",-1)),t("div",sa,[a[96]||(a[96]=t("p",{class:"small text-muted mb-3"},[e("Use the image URL directly in an "),t("code",null,"<img>"),e(" tag. You can also use just the path (without the domain) since the report renders on the same origin.")],-1)),t("div",da,[a[93]||(a[93]=t("div",{class:"step-label"},"Basic image",-1)),t("pre",la,s(d.image_basic),1)]),t("div",oa,[a[94]||(a[94]=t("div",{class:"step-label"},"Logo in a report header",-1)),t("pre",ra,s(d.image_header),1)]),t("div",ia,[a[95]||(a[95]=t("div",{class:"step-label"},"Sized and styled",-1)),t("pre",ba,s(d.image_styled),1)])])]),a[99]||(a[99]=i('<div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-7fb71b32></i>Limitations</div><div class="card-body" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Works</th><th data-v-7fb71b32>Does not work</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>&lt;img src=&quot;img:IMAGE_ID&quot;&gt;</code></td><td data-v-7fb71b32><code data-v-7fb71b32>background-image: url(/api/v1/images/ID/data)</code></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Standard <code data-v-7fb71b32>&lt;img&gt;</code> tags with inline styles</td><td data-v-7fb71b32>CSS <code data-v-7fb71b32>url()</code> references to gallery images (blocked by sanitizer)</td></tr></tbody></table><p class="small text-muted mt-2 mb-0" data-v-7fb71b32> The template CSS sanitizer strips non-<code data-v-7fb71b32>data:</code> URLs in stylesheets for security. Use <code data-v-7fb71b32>&lt;img&gt;</code> tags instead of CSS background images. </p></div></div><div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-info-circle me-2 text-info" data-v-7fb71b32></i>Tips</div><div class="card-body" data-v-7fb71b32><ul class="small mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Each project can hold up to <strong data-v-7fb71b32>20 images</strong>, each up to <strong data-v-7fb71b32>2 MB</strong>.</li><li class="mb-2" data-v-7fb71b32>Images are served with a 24-hour browser cache header, so they load quickly in previews.</li><li class="mb-2" data-v-7fb71b32>Use the <strong data-v-7fb71b32>Rename</strong> button to give images descriptive names for easy identification.</li><li data-v-7fb71b32>For logos and icons, <strong data-v-7fb71b32>SVG</strong> or <strong data-v-7fb71b32>WebP</strong> formats give the best quality-to-size ratio.</li></ul></div></div>',2))])):n("",!0),o.value==="markdown"?(b(),r("div",na,[a[115]||(a[115]=i('<h4 class="section-title" data-v-7fb71b32><i class="bi bi-markdown me-2 text-primary" data-v-7fb71b32></i>Markdown Templates</h4><p class="text-muted" data-v-7fb71b32>Markdown templates let you write reports in GitHub Flavoured Markdown (GFM) combined with Mustache syntax. The editor switches to a Markdown language mode, and both the live preview and server-side renders parse the Markdown before display.</p><div class="row g-4 mb-4" data-v-7fb71b32><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-check-circle me-2 text-success" data-v-7fb71b32></i>When to use Markdown</div><div class="card-body" data-v-7fb71b32><ul class="small mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Text-heavy reports — summaries, memos, executive briefings</li><li class="mb-2" data-v-7fb71b32>Simple tables from query data without custom styling</li><li class="mb-2" data-v-7fb71b32>Reports where you want to write content quickly without HTML boilerplate</li><li data-v-7fb71b32>Situations where the AI assistant&#39;s output is primarily prose</li></ul></div></div></div><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-x-circle me-2 text-danger" data-v-7fb71b32></i>When to use HTML instead</div><div class="card-body" data-v-7fb71b32><ul class="small mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Multi-column layouts with Bootstrap grid</li><li class="mb-2" data-v-7fb71b32>Precise per-page styling with custom CSS</li><li class="mb-2" data-v-7fb71b32>KPI tiles or complex badge styling requiring custom CSS</li><li data-v-7fb71b32>Reports that require <code data-v-7fb71b32>.report-page</code> divs with controlled page breaks</li></ul></div></div></div></div>',3)),t("div",ca,[a[106]||(a[106]=t("div",{class:"card-header"},[t("i",{class:"bi bi-braces me-2"}),e("Mustache works the same way")],-1)),t("div",va,[t("p",pa,[a[100]||(a[100]=e("All Mustache syntax — ",-1)),t("code",null,s(l.variable),1),a[101]||(a[101]=e(", ",-1)),t("code",null,s(l.section),1),a[102]||(a[102]=e(", ",-1)),t("code",null,s(l.inverted),1),a[103]||(a[103]=e(", dot notation — is evaluated first, then the result is parsed as Markdown. The ",-1)),t("code",null,s(l.rows_open),1),a[104]||(a[104]=e(" / ",-1)),t("code",null,s(l.rows_close),1),a[105]||(a[105]=e(" pattern still applies.",-1))]),t("pre",ma,s(d.markdown_basic),1)])]),t("div",ua,[a[111]||(a[111]=t("div",{class:"card-header"},[t("i",{class:"bi bi-table me-2"}),e("GFM tables with dynamic rows")],-1)),t("div",fa,[t("p",ga,[a[107]||(a[107]=e("Place the ",-1)),t("code",null,s(l.rows_open),1),a[108]||(a[108]=e(" loop inside the table body. Each iteration appends a row. Note: the closing ",-1)),t("code",null,s(l.rows_close),1),a[109]||(a[109]=e(" must sit on its own line.",-1))]),t("pre",ha,s(d.markdown_table),1),a[110]||(a[110]=t("div",{class:"alert alert-info mt-3 mb-0 py-2"},[t("i",{class:"bi bi-info-circle me-2"}),e(" Do not put blank lines between the pipe rows — GFM interprets a blank line as the end of the table. ")],-1))])]),a[116]||(a[116]=i('<div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-file-break me-2" data-v-7fb71b32></i>Page breaks</div><div class="card-body" data-v-7fb71b32><p class="small text-muted mb-2" data-v-7fb71b32>Inline HTML is allowed inside Markdown templates. Use the <code data-v-7fb71b32>.page-break</code> magic class to insert a page break — it works in browser preview, PDF export, and scheduled email delivery:</p><pre class="code-block" data-v-7fb71b32>&lt;div class=&quot;page-break&quot;&gt;&lt;/div&gt;</pre><p class="small text-muted mt-2 mb-0" data-v-7fb71b32>See the <strong data-v-7fb71b32>Pagination Magic</strong> section for the full set of layout commands (page-break-before, no-break, data-break-after, global headers/footers, and multi-column layouts).</p></div></div>',1)),t("div",ya,[a[114]||(a[114]=t("div",{class:"card-header"},[t("i",{class:"bi bi-bar-chart me-2"}),e("Charts in Markdown templates")],-1)),t("div",wa,[a[112]||(a[112]=t("p",{class:"small text-muted mb-3"},[e("Chart divs work inside Markdown templates via inline HTML passthrough. Paste a "),t("code",null,"report-bar-chart"),e(" or "),t("code",null,"report-pie-chart"),e(" div directly into your template — Mustache is evaluated first, then the chart is rendered as inline SVG before display.")],-1)),t("pre",ka,s(d.markdown_chart),1),a[113]||(a[113]=t("div",{class:"alert alert-success mt-3 mb-0 py-2"},[t("i",{class:"bi bi-check-circle me-2"}),e(" Charts render identically in browser preview, PDF export, and scheduled email delivery — no extra configuration required. ")],-1))])]),a[117]||(a[117]=i('<div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-list-check me-2" data-v-7fb71b32></i>Supported Markdown features</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Syntax</th><th data-v-7fb71b32>Output</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32># Heading</code> / <code data-v-7fb71b32>## H2</code> / <code data-v-7fb71b32>### H3</code></td><td data-v-7fb71b32>Heading elements</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>**bold**</code> / <code data-v-7fb71b32>*italic*</code></td><td data-v-7fb71b32>Strong / emphasis</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>- item</code> / <code data-v-7fb71b32>1. item</code></td><td data-v-7fb71b32>Unordered / ordered lists</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>- [x] done</code> / <code data-v-7fb71b32>- [ ] todo</code></td><td data-v-7fb71b32>Task list checkboxes</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>&gt; blockquote</code></td><td data-v-7fb71b32>Callout / pull-quote block</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>`code`</code> / <code data-v-7fb71b32>```block```</code></td><td data-v-7fb71b32>Inline / fenced code</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>| Col | Col |</code> + header separator</td><td data-v-7fb71b32>GFM table</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>---</code></td><td data-v-7fb71b32>Horizontal rule</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32>Inline HTML</td><td data-v-7fb71b32>Passed through (page breaks, images, charts, etc.)</td></tr></tbody></table></div></div>',1))])):n("",!0),o.value==="scheduling"?(b(),r("div",_a,[...a[118]||(a[118]=[i('<h4 class="section-title" data-v-7fb71b32><i class="bi bi-clock-history me-2 text-primary" data-v-7fb71b32></i>Scheduling</h4><p class="text-muted" data-v-7fb71b32>Schedules automate report rendering on a recurring basis using standard cron expressions. The app&#39;s service principal executes the query and renders the template server-side — no user session is required.</p><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-lightning me-2 text-warning" data-v-7fb71b32></i>Quick start</div><div class="card-body" data-v-7fb71b32><ol class="mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Make sure the app&#39;s service principal has <code data-v-7fb71b32>SELECT</code> privilege on every Unity Catalog table used by the report&#39;s data structure.</li><li class="mb-2" data-v-7fb71b32>Open <strong data-v-7fb71b32>Schedules</strong> from the sidebar (an active project must be selected).</li><li class="mb-2" data-v-7fb71b32>Click <strong data-v-7fb71b32>New Schedule</strong>, choose a data structure and template, set a frequency, and click <strong data-v-7fb71b32>Create Schedule</strong>.</li><li class="mb-2" data-v-7fb71b32>The schedule is registered immediately. Use the <i class="bi bi-play-fill" data-v-7fb71b32></i> button to trigger a test run without waiting for the next cron tick.</li><li data-v-7fb71b32>Switch to the <strong data-v-7fb71b32>Execution History</strong> tab and click <i class="bi bi-list-check" data-v-7fb71b32></i> on any schedule to review past runs and error messages.</li></ol></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-7fb71b32></i>Service principal requirement</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32> Scheduled executions run in the background without a user session. The app queries Databricks using the <strong data-v-7fb71b32>service principal credentials</strong> configured in the environment (<code data-v-7fb71b32>DATABRICKS_CLIENT_ID</code> / <code data-v-7fb71b32>DATABRICKS_CLIENT_SECRET</code> or <code data-v-7fb71b32>DATABRICKS_TOKEN</code>). </p><p class="small mb-0 text-danger fw-semibold" data-v-7fb71b32> If the service principal does not have <code data-v-7fb71b32>SELECT</code> on the relevant UC tables, every scheduled execution will fail with a permissions error. </p></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-calendar-week me-2" data-v-7fb71b32></i>Cron expression format</div><div class="card-body" data-v-7fb71b32><p class="small text-muted mb-3" data-v-7fb71b32>Schedules use standard 5-field cron syntax: <code data-v-7fb71b32>minute hour day month day_of_week</code>.</p><table class="table table-sm mb-3" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Expression</th><th data-v-7fb71b32>Meaning</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>0 9 * * *</code></td><td data-v-7fb71b32>Every day at 09:00</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>0 9 * * 1-5</code></td><td data-v-7fb71b32>Weekdays (Mon–Fri) at 09:00</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>0 8 * * 1</code></td><td data-v-7fb71b32>Every Monday at 08:00</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>0 6 1 * *</code></td><td data-v-7fb71b32>1st of every month at 06:00</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>*/15 * * * *</code></td><td data-v-7fb71b32>Every 15 minutes</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>30 17 * * 5</code></td><td data-v-7fb71b32>Every Friday at 17:30</td></tr></tbody></table><p class="small text-muted mb-0" data-v-7fb71b32> The schedule builder&#39;s <strong data-v-7fb71b32>Simple</strong> mode generates a cron expression for you. Switch to <strong data-v-7fb71b32>Cron</strong> mode to enter one manually. </p></div></div><div class="card mb-4" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-list-check me-2" data-v-7fb71b32></i>Execution statuses</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Status</th><th data-v-7fb71b32>Meaning</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge bg-primary" data-v-7fb71b32>running</span></td><td data-v-7fb71b32>The execution is in progress. The history panel auto-refreshes every 10 seconds while a run is active.</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>success</span></td><td data-v-7fb71b32>The report rendered without error.</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge bg-danger" data-v-7fb71b32>failed</span></td><td data-v-7fb71b32>The run failed — check the <strong data-v-7fb71b32>Error</strong> column for details (missing UC privilege, bad Mustache syntax, warehouse timeout, etc.).</td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><span class="badge bg-secondary" data-v-7fb71b32>pending</span></td><td data-v-7fb71b32>Queued but not yet started.</td></tr></tbody></table></div></div><div class="row g-4 mb-4" data-v-7fb71b32><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-pencil me-2 text-primary" data-v-7fb71b32></i>Editing a schedule</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>Click the <i class="bi bi-pencil" data-v-7fb71b32></i> button to change a schedule&#39;s <strong data-v-7fb71b32>name</strong>, <strong data-v-7fb71b32>cron expression</strong>, or <strong data-v-7fb71b32>active</strong> status.</p><p class="small mb-2" data-v-7fb71b32>The linked structure and template cannot be changed after creation — delete and recreate the schedule if you need a different template.</p><p class="small mb-0 text-muted" data-v-7fb71b32>Saving a cron change re-registers the APScheduler job immediately.</p></div></div></div><div class="col-md-6" data-v-7fb71b32><div class="card h-100" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-toggle-on me-2 text-success" data-v-7fb71b32></i>Active vs Inactive</div><div class="card-body" data-v-7fb71b32><p class="small mb-2" data-v-7fb71b32>Inactive schedules are not registered with the scheduler — they will not fire automatically.</p><p class="small mb-2" data-v-7fb71b32>Toggling a schedule back to <strong data-v-7fb71b32>Active</strong> immediately re-registers the cron job with no further action required.</p><p class="small mb-0 text-muted" data-v-7fb71b32>The manual trigger button (<i class="bi bi-play-fill" data-v-7fb71b32></i>) works regardless of the active flag.</p></div></div></div></div><div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-info-circle me-2 text-info" data-v-7fb71b32></i>Tips &amp; limitations</div><div class="card-body" data-v-7fb71b32><ul class="small mb-0" data-v-7fb71b32><li class="mb-2" data-v-7fb71b32>Schedules are scoped to a project — select the project in the sidebar before navigating to the Schedules page.</li><li class="mb-2" data-v-7fb71b32>The scheduler runs in the same process as the FastAPI back-end. If the app restarts, all active schedules are automatically re-registered from the database on startup.</li><li class="mb-2" data-v-7fb71b32>Execution history is paginated to the last 50 runs by default. Use the offset/limit query parameters on the API if you need older entries.</li><li class="mb-2" data-v-7fb71b32>Only the project owner and shared members can create or modify schedules. The <code data-v-7fb71b32>check_schedule_project_access</code> guard applies the same access + lock rules as structures and templates.</li><li data-v-7fb71b32>Scheduled renders use a <strong data-v-7fb71b32>10,000 row limit</strong> on the SQL query — the same as a full PDF export.</li></ul></div></div>',8)])])):n("",!0),o.value==="pagination"?(b(),r("div",xa,[a[133]||(a[133]=t("h4",{class:"section-title"},[t("i",{class:"bi bi-layout-text-sidebar-reverse me-2 text-primary"}),e("Pagination Magic Commands")],-1)),a[134]||(a[134]=t("p",{class:"text-muted"},"Special classes and attributes processed by both the live preview and the server-side PDF/email pipeline. All commands work in HTML templates and via inline HTML passthrough in Markdown templates.",-1)),t("div",Sa,[a[120]||(a[120]=t("div",{class:"card-header"},[t("i",{class:"bi bi-file-break me-2"}),e("Page break commands")],-1)),t("div",Ta,[a[119]||(a[119]=i('<p class="small text-muted mb-3" data-v-7fb71b32>Place invisible magic divs to control exactly where pages break. Visual indicators appear in the live preview.</p><div class="row g-3 mb-3" data-v-7fb71b32><div class="col-md-6" data-v-7fb71b32><div class="p-3 bg-light rounded h-100" data-v-7fb71b32><div class="fw-semibold small mb-1" data-v-7fb71b32><code data-v-7fb71b32>.page-break</code></div><p class="small text-muted mb-0" data-v-7fb71b32>Forces a page break <strong data-v-7fb71b32>after</strong> this point. Content below moves to the next page.</p></div></div><div class="col-md-6" data-v-7fb71b32><div class="p-3 bg-light rounded h-100" data-v-7fb71b32><div class="fw-semibold small mb-1" data-v-7fb71b32><code data-v-7fb71b32>.page-break-before</code></div><p class="small text-muted mb-0" data-v-7fb71b32>Forces a page break <strong data-v-7fb71b32>before</strong> the following content block.</p></div></div></div>',2)),t("pre",Ca,s(d.pagination_break_after),1)])]),t("div",Aa,[a[122]||(a[122]=t("div",{class:"card-header"},[t("i",{class:"bi bi-lock me-2"}),e("Keeping blocks together ("),t("code",null,".no-break"),e(")")],-1)),t("div",Ra,[a[121]||(a[121]=t("p",{class:"small text-muted mb-3"},[e("Wrap any element in "),t("code",null,".no-break"),e(" to prevent it from being split across pages. Useful for headings with their opening paragraph, or KPI tiles that should stay together.")],-1)),t("pre",Ma,s(d.pagination_no_break),1)])]),t("div",qa,[a[126]||(a[126]=t("div",{class:"card-header"},[t("i",{class:"bi bi-layout-split me-2"}),e("Auto page break every N rows ("),t("code",null,"data-break-after"),e(")")],-1)),t("div",Pa,[a[123]||(a[123]=t("p",{class:"small text-muted mb-3"},[e("Wrap a Mustache loop in a container with "),t("code",null,'data-break-after="N"'),e(". After rendering, the pipeline counts direct child elements and automatically injects a "),t("code",null,".page-break"),e(" after every N-th one — no manual counting needed.")],-1)),t("pre",Ea,s(d.pagination_break_after_n),1),a[124]||(a[124]=t("p",{class:"small text-muted mt-3 mb-2"},"Works equally well with table rows:",-1)),t("pre",ja,s(d.pagination_break_after_table),1),a[125]||(a[125]=t("div",{class:"alert alert-info mt-3 mb-0 py-2"},[t("i",{class:"bi bi-info-circle me-2"}),e(" The trailing group (the last partial batch of rows) never gets a page break appended — the renderer handles this automatically. ")],-1))])]),t("div",La,[a[129]||(a[129]=t("div",{class:"card-header"},[t("i",{class:"bi bi-textarea-t me-2"}),e("Repeating header & footer ("),t("code",null,".report-global-header"),e(" / "),t("code",null,".report-global-footer"),e(")")],-1)),t("div",Ia,[a[127]||(a[127]=i('<p class="small text-muted mb-3" data-v-7fb71b32>Define <code data-v-7fb71b32>.report-global-header</code> and/or <code data-v-7fb71b32>.report-global-footer</code> <strong data-v-7fb71b32>once</strong> — outside any <code data-v-7fb71b32>.report-page</code> div. The renderer automatically removes them from their original position and injects a copy at the top and bottom of <strong data-v-7fb71b32>every</strong> <code data-v-7fb71b32>.report-page</code>. Headers and footers can contain Mustache, charts, and image references.</p>',1)),t("pre",Da,s(d.pagination_global_header),1),a[128]||(a[128]=t("div",{class:"alert alert-warning mt-3 mb-0 py-2"},[t("i",{class:"bi bi-exclamation-triangle me-2"}),e(" This feature only works in templates that use explicit "),t("code",null,'<div class="report-page">'),e(" divs. Markdown templates require inline "),t("code",null,"<div>"),e(" passthrough for page wrappers. ")],-1))])]),t("div",Ua,[a[132]||(a[132]=t("div",{class:"card-header"},[t("i",{class:"bi bi-layout-three-columns me-2"}),e("Multi-column layouts")],-1)),t("div",Fa,[a[130]||(a[130]=t("p",{class:"small text-muted mb-3"},[e("Use "),t("code",null,".report-columns-2"),e(", "),t("code",null,".report-columns-3"),e(", or "),t("code",null,".report-columns-4"),e(" to flow content into newspaper-style columns using CSS "),t("code",null,"column-count"),e(". Works in both browser preview and WeasyPrint PDF.")],-1)),t("pre",Ha,s(d.pagination_columns),1),a[131]||(a[131]=t("div",{class:"alert alert-info mt-3 mb-0 py-2"},[t("i",{class:"bi bi-info-circle me-2"}),e(" Chart divs inside multi-column containers may not render at the expected size — place charts outside column wrappers where possible. ")],-1))])]),a[135]||(a[135]=i('<div class="card" data-v-7fb71b32><div class="card-header" data-v-7fb71b32><i class="bi bi-table me-2" data-v-7fb71b32></i>Quick reference</div><div class="card-body p-0" data-v-7fb71b32><table class="table table-sm mb-0" data-v-7fb71b32><thead class="table-dark" data-v-7fb71b32><tr data-v-7fb71b32><th data-v-7fb71b32>Element</th><th data-v-7fb71b32>Effect</th><th data-v-7fb71b32>Works in Markdown?</th></tr></thead><tbody data-v-7fb71b32><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>&lt;div class=&quot;page-break&quot;&gt;</code></td><td data-v-7fb71b32>Page break after</td><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>Yes</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>&lt;div class=&quot;page-break-before&quot;&gt;</code></td><td data-v-7fb71b32>Page break before</td><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>Yes</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>&lt;div class=&quot;no-break&quot;&gt;</code></td><td data-v-7fb71b32>Prevent split across pages</td><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>Yes</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>data-break-after=&quot;N&quot;</code></td><td data-v-7fb71b32>Auto break every N child elements</td><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>Yes</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>.report-global-header</code></td><td data-v-7fb71b32>Cloned into top of every .report-page</td><td data-v-7fb71b32><span class="badge bg-warning text-dark" data-v-7fb71b32>Requires page divs</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>.report-global-footer</code></td><td data-v-7fb71b32>Cloned into bottom of every .report-page</td><td data-v-7fb71b32><span class="badge bg-warning text-dark" data-v-7fb71b32>Requires page divs</span></td></tr><tr data-v-7fb71b32><td data-v-7fb71b32><code data-v-7fb71b32>.report-columns-2 / -3 / -4</code></td><td data-v-7fb71b32>Multi-column flow layout</td><td data-v-7fb71b32><span class="badge bg-success" data-v-7fb71b32>Yes</span></td></tr></tbody></table></div></div>',1))])):n("",!0)])])]))}}),Wa=h(Na,[["__scopeId","data-v-7fb71b32"]]);export{Wa as default};
