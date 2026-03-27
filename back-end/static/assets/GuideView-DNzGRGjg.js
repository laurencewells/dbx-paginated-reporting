import{d as m,c as r,a as d,b as e,F as f,v as b,e as c,y as n,x as a,D as h,o,w as p,_ as g}from"./index-jKusvrPx.js";const y={class:"guide-view"},w={class:"row g-4"},_={class:"col-md-3"},k={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},x={class:"card-body p-2"},S=["onClick"],T={class:"col-md-9"},C={key:0},A={key:1},R={class:"card mb-4"},M={class:"card-body p-0"},q={class:"table table-sm mb-0"},E={class:"syntax-tag"},j={class:"syntax-tag"},P={class:"syntax-tag"},L={class:"syntax-tag"},I={class:"syntax-tag"},D={class:"syntax-tag"},U={class:"alert alert-warning"},H={class:"ms-1"},F={class:"card"},G={class:"card-body"},N={class:"code-block"},O={class:"mb-0 small text-muted mt-2"},V={key:2},Q={class:"pattern-step"},B={class:"code-block"},Y={class:"pattern-step"},W={class:"code-block"},z={class:"pattern-step"},K={class:"code-block"},$={class:"alert alert-info"},J={key:3},X={class:"pattern-step"},Z={class:"code-block"},dd={class:"pattern-step"},td={class:"code-block"},ed={class:"pattern-step"},ad={class:"row g-3"},sd={class:"col-md-6"},ld={class:"approach-card"},id={class:"code-block"},rd={class:"small text-muted mt-2 mb-0"},od={class:"col-md-6"},cd={class:"approach-card"},nd={class:"code-block"},vd={key:4},pd={class:"pattern-step"},ud={class:"code-block"},md={class:"pattern-step"},fd={class:"code-block"},bd={class:"pattern-step"},hd={class:"code-block"},gd={class:"alert alert-info"},yd={key:5},wd={class:"pattern-card mb-4"},_d={class:"card-body"},kd={class:"code-block"},xd={class:"pattern-card mb-4"},Sd={class:"card-body"},Td={class:"code-block"},Cd={class:"pattern-card mb-4"},Ad={class:"card-body"},Rd={class:"pattern-step"},Md={class:"code-block"},qd={class:"pattern-step"},Ed={class:"code-block"},jd={class:"pattern-step"},Pd={class:"code-block"},Ld={class:"card mb-4"},Id={class:"card-body"},Dd={class:"code-block"},Ud={class:"card"},Hd={class:"card-body"},Fd={class:"code-block"},Gd={key:6},Nd={class:"pattern-card mb-4"},Od={class:"card-body"},Vd={class:"pattern-step"},Qd={class:"code-block"},Bd={class:"pattern-step"},Yd={class:"code-block"},Wd={class:"alert alert-success mb-0"},zd={class:"pattern-card mb-4"},Kd={class:"card-body"},$d={class:"small text-muted mb-3"},Jd={class:"pattern-step"},Xd={class:"code-block"},Zd={class:"pattern-step"},dt={class:"code-block"},tt={key:7},et={class:"pattern-card mb-4"},at={class:"card-body"},st={class:"pattern-step"},lt={class:"code-block"},it={class:"pattern-step"},rt={class:"code-block"},ot={class:"pattern-step"},ct={class:"code-block"},nt={key:8},vt={class:"card mb-4"},pt={class:"card-body"},ut={class:"small text-muted mb-3"},mt={class:"code-block"},ft={class:"card mb-4"},bt={class:"card-body"},ht={class:"small text-muted mb-3"},gt={class:"code-block"},yt={class:"card mb-4"},wt={class:"card-body"},_t={class:"code-block"},kt={key:9},xt=m({__name:"GuideView",setup(St){const i=h("projects"),u=[{id:"projects",label:"Projects",icon:"bi-folder2-open"},{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"},{id:"images",label:"Images",icon:"bi-images"},{id:"markdown",label:"Markdown Templates",icon:"bi-markdown"},{id:"scheduling",label:"Scheduling",icon:"bi-clock-history"}],s={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},l={dataShape:`{
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

<div style="page-break-after: always"></div>
{{/rows}}`,markdown_table:`| Name | Department | Status |
|------|-----------|--------|
{{#rows}}| {{name}} | {{department}} | {{status}} |
{{/rows}}`,image_basic:'<img src="img:IMAGE_ID" alt="Description" />',image_header:`<div class="report-page">
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
</div>`};return(Tt,t)=>(o(),r("div",y,[t[119]||(t[119]=d("div",{class:"guide-header mb-4"},[d("h2",{class:"mb-1"},[d("i",{class:"bi bi-book text-primary me-2"}),e(" Template Guide ")]),d("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),d("div",w,[d("div",_,[d("div",k,[d("div",x,[(o(),r(f,null,b(u,v=>d("button",{key:v.id,class:p(["guide-nav-btn",{active:i.value===v.id}]),onClick:Ct=>i.value=v.id},[d("i",{class:p(["bi",v.icon,"me-2"])},null,2),e(" "+a(v.label),1)],10,S)),64))])])]),d("div",T,[i.value==="projects"?(o(),r("div",C,[...t[0]||(t[0]=[c('<h4 class="section-title" data-v-cf83ded4><i class="bi bi-folder2-open me-2 text-primary" data-v-cf83ded4></i>Projects</h4><p class="text-muted" data-v-cf83ded4>Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-lightning me-2 text-warning" data-v-cf83ded4></i>Getting started</div><div class="card-body" data-v-cf83ded4><ol class="mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Navigate to <strong data-v-cf83ded4>Projects</strong> and click <strong data-v-cf83ded4>New Project</strong>.</li><li class="mb-2" data-v-cf83ded4>Give it a name (e.g. &quot;Q1 Sales Reports&quot;) and click <strong data-v-cf83ded4>Create</strong>.</li><li class="mb-2" data-v-cf83ded4>Click <strong data-v-cf83ded4>Open</strong> to set it as your active project — you&#39;ll see a banner in the sidebar.</li><li class="mb-2" data-v-cf83ded4>Now go to <strong data-v-cf83ded4>Data Structures</strong> — any structures you create will automatically belong to this project.</li><li data-v-cf83ded4>Create templates linked to those structures, then use the <strong data-v-cf83ded4>Export</strong> button in the Template Editor to preview with real data (configurable row count) and export to PDF.</li></ol></div></div><div class="row g-4 mb-4" data-v-cf83ded4><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-diagram-3 me-2 text-primary" data-v-cf83ded4></i>How structures are linked</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>When a project is active, new structures are automatically associated with it via a <code data-v-cf83ded4>project_id</code> field.</p><p class="small mb-2" data-v-cf83ded4>The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p><p class="small mb-0 text-muted" data-v-cf83ded4>Clear the project filter (click the <i class="bi bi-x-lg" data-v-cf83ded4></i> in the sidebar banner) to see all structures across all projects.</p></div></div></div><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-file-code me-2 text-success" data-v-cf83ded4></i>How templates are linked</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>Templates don&#39;t have a direct project link — they&#39;re associated through their <strong data-v-cf83ded4>structure</strong>.</p><p class="small mb-0" data-v-cf83ded4>When filtering by project, the app shows templates whose linked structure belongs to the active project.</p></div></div></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-lock me-2 text-warning" data-v-cf83ded4></i>Locking</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>Only the project <strong data-v-cf83ded4>owner</strong> can lock or unlock a project.</p><p class="small mb-2" data-v-cf83ded4>When a project is <strong data-v-cf83ded4>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code data-v-cf83ded4>423 Locked</code> response.</p><p class="small mb-0 text-muted" data-v-cf83ded4>This is useful when a report set is finalised and you want to prevent accidental edits.</p></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-people me-2 text-info" data-v-cf83ded4></i>Sharing</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>Share a project with colleagues by entering their email address on the project detail panel.</p><p class="small mb-2" data-v-cf83ded4>Shared users can <strong data-v-cf83ded4>view</strong> and <strong data-v-cf83ded4>edit</strong> structures and templates in the project (unless it&#39;s locked).</p><p class="small mb-2" data-v-cf83ded4>Only the project <strong data-v-cf83ded4>owner</strong> can:</p><ul class="small mb-0" data-v-cf83ded4><li data-v-cf83ded4>Lock / unlock the project</li><li data-v-cf83ded4>Add or remove shares</li><li data-v-cf83ded4>Delete the project</li></ul></div></div><div class="card" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-table me-2" data-v-cf83ded4></i>Permission summary</div><div class="card-body p-0" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Action</th><th data-v-cf83ded4>Owner</th><th data-v-cf83ded4>Shared user</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4>View structures &amp; templates</td><td class="text-success" data-v-cf83ded4>Yes</td><td class="text-success" data-v-cf83ded4>Yes</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Create / edit / delete structures &amp; templates</td><td class="text-success" data-v-cf83ded4>Yes (if unlocked)</td><td class="text-success" data-v-cf83ded4>Yes (if unlocked)</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Lock / unlock project</td><td class="text-success" data-v-cf83ded4>Yes</td><td class="text-danger" data-v-cf83ded4>No</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Share / unshare project</td><td class="text-success" data-v-cf83ded4>Yes</td><td class="text-danger" data-v-cf83ded4>No</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Delete project</td><td class="text-success" data-v-cf83ded4>Yes</td><td class="text-danger" data-v-cf83ded4>No</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Rename project</td><td class="text-success" data-v-cf83ded4>Yes</td><td class="text-danger" data-v-cf83ded4>No</td></tr></tbody></table></div></div>',7)])])):n("",!0),i.value==="mustache"?(o(),r("div",A,[t[21]||(t[21]=d("h4",{class:"section-title"},[d("i",{class:"bi bi-braces me-2 text-primary"}),e("Mustache Syntax Reference")],-1)),t[22]||(t[22]=d("p",{class:"text-muted"},[e("Mustache is a logic-less templating language. All data comes from the "),d("code",null,"rows"),e(" array returned by your SQL query.")],-1)),d("div",R,[d("div",M,[d("table",q,[t[10]||(t[10]=d("thead",{class:"table-dark"},[d("tr",null,[d("th",null,"Syntax"),d("th",null,"Purpose"),d("th",null,"Example")])],-1)),d("tbody",null,[d("tr",null,[d("td",null,[d("code",E,a(s.variable),1)]),t[1]||(t[1]=d("td",null,"Render a value (HTML-escaped)",-1)),d("td",null,[d("code",null,a(s.ex_field),1)])]),d("tr",null,[d("td",null,[d("code",j,a(s.triple),1)]),t[2]||(t[2]=d("td",null,"Render raw HTML (unescaped)",-1)),d("td",null,[d("code",null,a(s.triple),1)])]),d("tr",null,[d("td",null,[d("code",P,a(s.section),1)]),t[3]||(t[3]=d("td",null,[e("Iterate array "),d("strong",null,"or"),e(" render if truthy")],-1)),d("td",null,[d("code",null,a(s.rows_open)+"..."+a(s.rows_close),1)])]),d("tr",null,[d("td",null,[d("code",L,a(s.inverted),1)]),t[4]||(t[4]=d("td",null,"Render if falsy or empty",-1)),d("td",null,[d("code",null,a(s.delete_check),1)])]),d("tr",null,[d("td",null,[d("code",I,a(s.dot),1)]),t[8]||(t[8]=d("td",null,[e("Current item in a "),d("em",null,"scalar"),e(" list only")],-1)),d("td",null,[d("code",null,a(s.ex_dot_loop),1),t[5]||(t[5]=e(" (tags is ",-1)),t[6]||(t[6]=d("code",null,'["a","b"]',-1)),t[7]||(t[7]=e(")",-1))])]),d("tr",null,[d("td",null,[d("code",D,a(s.comment),1)]),t[9]||(t[9]=d("td",null,"Comment — not rendered",-1)),d("td",null,[d("code",null,a(s.ex_comment),1)])])])])])]),d("div",U,[t[11]||(t[11]=d("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),t[12]||(t[12]=d("strong",null,"Closing tags must always match the opening name exactly.",-1)),d("code",H,a(s.rows_open),1),t[13]||(t[13]=e(" closes with ",-1)),d("code",null,a(s.rows_close),1),t[14]||(t[14]=e(" — never ",-1)),d("code",null,a(s.rows_wrong),1),t[15]||(t[15]=e(". ",-1))]),d("div",F,[t[20]||(t[20]=d("div",{class:"card-header"},[d("i",{class:"bi bi-lightbulb me-2 text-warning"}),e("Key rule — your data is always "),d("code",null,"rows")],-1)),d("div",G,[t[19]||(t[19]=d("p",{class:"mb-2"},[e("Every query returns a single top-level key "),d("code",null,"rows"),e(", which is a list of objects:")],-1)),d("pre",N,a(l.dataShape),1),d("p",O,[t[16]||(t[16]=e("Each row also receives ",-1)),d("code",null,a(s.index),1),t[17]||(t[17]=e(" (1-based position) and ",-1)),d("code",null,a(s.total),1),t[18]||(t[18]=e(" (total row count) automatically.",-1))])])])])):n("",!0),i.value==="flat-table"?(o(),r("div",V,[t[30]||(t[30]=d("h4",{class:"section-title"},[d("i",{class:"bi bi-table me-2 text-primary"}),e("Flat Table Report")],-1)),t[31]||(t[31]=d("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),d("div",Q,[t[23]||(t[23]=d("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),d("pre",B,a(l.flatTable_sql),1)]),d("div",Y,[t[24]||(t[24]=d("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),d("pre",W,a(l.flatTable_data),1)]),d("div",z,[t[25]||(t[25]=d("div",{class:"step-label"},"3 · Mustache Template",-1)),d("pre",K,a(l.flatTable_template),1)]),d("div",$,[t[26]||(t[26]=d("i",{class:"bi bi-info-circle me-2"},null,-1)),t[27]||(t[27]=d("strong",null,"Null / empty check:",-1)),t[28]||(t[28]=e(" use ",-1)),d("code",null,a(s.inverted),1),t[29]||(t[29]=e(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),i.value==="struct"?(o(),r("div",J,[t[39]||(t[39]=d("h4",{class:"section-title"},[d("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),e("Struct Fields")],-1)),t[40]||(t[40]=d("p",{class:"text-muted"},[e("When a column is "),d("code",null,"STRUCT<...>"),e(", Mustache can push it as a context or access it with dot notation.")],-1)),d("div",X,[t[32]||(t[32]=d("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),d("pre",Z,a(l.struct_sql),1)]),d("div",dd,[t[33]||(t[33]=d("div",{class:"step-label"},"2 · Data Shape",-1)),d("pre",td,a(l.struct_data),1)]),d("div",ed,[t[38]||(t[38]=d("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),d("div",ad,[d("div",sd,[d("div",ld,[t[35]||(t[35]=d("div",{class:"approach-label"},"Context push (recommended)",-1)),d("pre",id,a(l.struct_context),1),d("p",rd,[d("code",null,a(s.address_open),1),t[34]||(t[34]=e(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),d("div",od,[d("div",cd,[t[36]||(t[36]=d("div",{class:"approach-label"},"Dot notation",-1)),d("pre",nd,a(l.struct_dot),1),t[37]||(t[37]=d("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),i.value==="array-struct"?(o(),r("div",vd,[t[52]||(t[52]=d("h4",{class:"section-title"},[d("i",{class:"bi bi-list-nested me-2 text-primary"}),e("Array of Structs")],-1)),t[53]||(t[53]=d("p",{class:"text-muted"},[e("When a column is "),d("code",null,"ARRAY<STRUCT<...>>"),e(", iterate the outer "),d("code",null,"rows"),e(" first, then the nested array inside.")],-1)),d("div",pd,[t[41]||(t[41]=d("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),d("pre",ud,a(l.array_sql),1)]),d("div",md,[t[42]||(t[42]=d("div",{class:"step-label"},"2 · Data Shape",-1)),d("pre",fd,a(l.array_data),1)]),d("div",bd,[t[43]||(t[43]=d("div",{class:"step-label"},"3 · Template — nested iteration",-1)),d("pre",hd,a(l.array_template),1)]),d("div",gd,[t[44]||(t[44]=d("i",{class:"bi bi-info-circle me-2"},null,-1)),t[45]||(t[45]=d("strong",null,"One page per order:",-1)),t[46]||(t[46]=e(" the outer ",-1)),d("code",null,a(s.rows_open),1),t[47]||(t[47]=e(" wraps a ",-1)),t[48]||(t[48]=d("code",null,".report-page",-1)),t[49]||(t[49]=e(" div, so each order gets its own page. ",-1)),d("code",null,a(s.index),1),t[50]||(t[50]=e(" and ",-1)),d("code",null,a(s.total),1),t[51]||(t[51]=e(" are available on each row. ",-1))])])):n("",!0),i.value==="chart-struct"?(o(),r("div",yd,[t[68]||(t[68]=c('<h4 class="section-title" data-v-cf83ded4><i class="bi bi-bar-chart me-2 text-primary" data-v-cf83ded4></i>Charts from Struct Columns</h4><div class="alert alert-success py-2 mb-3" data-v-cf83ded4><i class="bi bi-check-circle me-2" data-v-cf83ded4></i>Charts render as <strong data-v-cf83ded4>inline SVG</strong> — they display identically in the browser preview, PDF export, and email delivery. No JavaScript required at render time. </div><p class="text-muted" data-v-cf83ded4>Charts read comma-separated strings from <code data-v-cf83ded4>data-labels</code> and <code data-v-cf83ded4>data-values</code> attributes. There are three ways to feed data in.</p>',3)),d("div",wd,[t[56]||(t[56]=d("div",{class:"pattern-header pattern-1"},[e("Pattern 1 — Aggregate the main "),d("code",null,"rows"),e(" array (simplest)")],-1)),d("div",_d,[t[54]||(t[54]=d("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),d("pre",kd,a(l.chart1_template),1),t[55]||(t[55]=d("p",{class:"small text-muted mt-2 mb-0"},[e("Mustache renders the loops into: "),d("code",null,'data-labels="EMEA,APAC,AMER,"'),e(" — trailing commas are ignored by the parser.")],-1))])]),d("div",xd,[t[58]||(t[58]=d("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),d("div",Sd,[t[57]||(t[57]=d("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),d("pre",Td,a(l.chart2_template),1)])]),d("div",Cd,[t[64]||(t[64]=d("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),d("div",Ad,[t[62]||(t[62]=d("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),d("div",Rd,[t[59]||(t[59]=d("div",{class:"step-label"},"SQL",-1)),d("pre",Md,a(l.chart3_sql),1)]),d("div",qd,[t[60]||(t[60]=d("div",{class:"step-label"},"Data Shape",-1)),d("pre",Ed,a(l.chart3_data),1)]),d("div",jd,[t[61]||(t[61]=d("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),d("pre",Pd,a(l.chart3_template),1)]),t[63]||(t[63]=d("div",{class:"alert alert-success mb-0"},[d("i",{class:"bi bi-check-circle-fill me-2"}),d("strong",null,"Why this pattern is powerful:"),e(" each team's chart is driven entirely by its own "),d("code",null,"spend_by_month"),e(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),t[69]||(t[69]=c('<div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-table me-2" data-v-cf83ded4></i>Pattern comparison</div><div class="card-body p-0" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Pattern</th><th data-v-cf83ded4>SQL complexity</th><th data-v-cf83ded4>Best for</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge pattern-badge-1" data-v-cf83ded4>1 — Aggregate rows</span></td><td data-v-cf83ded4>Low</td><td data-v-cf83ded4>Single summary chart across all rows</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge pattern-badge-2" data-v-cf83ded4>2 — Scalar columns</span></td><td data-v-cf83ded4>Low–Medium</td><td data-v-cf83ded4>Fixed labels, one summary row</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge pattern-badge-3" data-v-cf83ded4>3 — Struct array</span></td><td data-v-cf83ded4>Medium</td><td data-v-cf83ded4>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-sliders me-2" data-v-cf83ded4></i>Optional chart attributes</div><div class="card-body" data-v-cf83ded4><p class="small text-muted mb-3" data-v-cf83ded4>All attributes are optional — existing chart divs work unchanged. Add them to customise appearance and behaviour without any template restructuring.</p><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Attribute</th><th data-v-cf83ded4>Applies to</th><th data-v-cf83ded4>Description</th><th data-v-cf83ded4>Example</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-title</code></td><td data-v-cf83ded4>bar, pie</td><td data-v-cf83ded4>Chart title rendered above the chart</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;Revenue by Region&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-color-scheme</code></td><td data-v-cf83ded4>bar, pie</td><td data-v-cf83ded4>Vega colour scheme name</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;blues&quot;</code>, <code data-v-cf83ded4>&quot;tableau10&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-width</code></td><td data-v-cf83ded4>bar, pie</td><td data-v-cf83ded4>Width in px (default: 500 bar / 300 pie)</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;400&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-height</code></td><td data-v-cf83ded4>bar, pie</td><td data-v-cf83ded4>Height in px (default: 250 bar / 300 pie)</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;200&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-x-title</code></td><td data-v-cf83ded4>bar</td><td data-v-cf83ded4>X-axis label</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;Quarter&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-y-title</code></td><td data-v-cf83ded4>bar</td><td data-v-cf83ded4>Y-axis label</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;Revenue ($)&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-sort</code></td><td data-v-cf83ded4>bar</td><td data-v-cf83ded4>Sort bars: <code data-v-cf83ded4>ascending</code>, <code data-v-cf83ded4>descending</code></td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;descending&quot;</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>data-inner-radius</code></td><td data-v-cf83ded4>pie</td><td data-v-cf83ded4>Inner radius in px — <code data-v-cf83ded4>0</code> = pie (default), <code data-v-cf83ded4>&gt;0</code> = donut</td><td data-v-cf83ded4><code data-v-cf83ded4>&quot;50&quot;</code></td></tr></tbody></table></div></div>',2)),d("div",Ld,[t[65]||(t[65]=d("div",{class:"card-header"},[d("i",{class:"bi bi-bar-chart me-2"}),e("Example: titled bar chart with colour scheme")],-1)),d("div",Id,[d("pre",Dd,a(l.chart_opts_bar),1)])]),d("div",Ud,[t[67]||(t[67]=d("div",{class:"card-header"},[d("i",{class:"bi bi-pie-chart me-2"}),e("Example: donut chart")],-1)),d("div",Hd,[t[66]||(t[66]=d("p",{class:"small text-muted mb-3"},[e("Set "),d("code",null,"data-inner-radius"),e(" to any positive value to turn a pie chart into a donut. A value of "),d("code",null,"50"),e(" is a good starting point.")],-1)),d("pre",Fd,a(l.chart_opts_donut),1)])])])):n("",!0),i.value==="conditional-styles"?(o(),r("div",Gd,[t[90]||(t[90]=d("h4",{class:"section-title"},[d("i",{class:"bi bi-palette me-2 text-primary"}),e("Conditional Styles")],-1)),t[91]||(t[91]=d("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),d("div",Nd,[t[83]||(t[83]=d("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),d("div",Od,[t[82]||(t[82]=d("p",{class:"small text-muted mb-3"},[e(" Interpolate the field value directly into the class name. Add a "),d("code",null,"<style>"),e(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),d("div",Vd,[t[70]||(t[70]=d("div",{class:"step-label"},"SQL — no changes needed",-1)),d("pre",Qd,a(l.conditional_sql_pattern1),1)]),d("div",Bd,[t[71]||(t[71]=d("div",{class:"step-label"},"Template",-1)),d("pre",Yd,a(l.conditional_template_pattern1),1)]),d("div",Wd,[t[72]||(t[72]=d("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),t[73]||(t[73]=d("strong",null,"How it works:",-1)),t[74]||(t[74]=e()),d("code",null,a(s.cond_class_example),1),t[75]||(t[75]=e(" renders as ",-1)),t[76]||(t[76]=d("code",null,"status-approved",-1)),t[77]||(t[77]=e(", ",-1)),t[78]||(t[78]=d("code",null,"status-pending",-1)),t[79]||(t[79]=e(", or ",-1)),t[80]||(t[80]=d("code",null,"status-rejected",-1)),t[81]||(t[81]=e(". Your CSS rules match on those exact class names. ",-1))])])]),d("div",zd,[t[89]||(t[89]=d("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),d("div",Kd,[d("p",$d,[t[84]||(t[84]=e(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),d("code",null,a(s.section),1),t[85]||(t[85]=e(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),d("div",Jd,[t[86]||(t[86]=d("div",{class:"step-label"},"SQL — add boolean columns",-1)),d("pre",Xd,a(l.conditional_sql_pattern2),1)]),d("div",Zd,[t[87]||(t[87]=d("div",{class:"step-label"},"Template — conditional blocks",-1)),d("pre",dt,a(l.conditional_template_pattern2),1)]),t[88]||(t[88]=d("div",{class:"alert alert-info mb-0"},[d("i",{class:"bi bi-info-circle me-2"}),d("strong",null,"When to use Pattern 2:"),e(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),t[92]||(t[92]=c('<div class="card" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-table me-2" data-v-cf83ded4></i>Pattern comparison</div><div class="card-body p-0" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Pattern</th><th data-v-cf83ded4>SQL change?</th><th data-v-cf83ded4>Best for</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge pattern-badge-1" data-v-cf83ded4>1 — CSS class from value</span></td><td data-v-cf83ded4>None</td><td data-v-cf83ded4>Badge colours, row highlights, status indicators</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge pattern-badge-2" data-v-cf83ded4>2 — SQL boolean flags</span></td><td data-v-cf83ded4>Add <code data-v-cf83ded4>field = &#39;value&#39; AS is_x</code></td><td data-v-cf83ded4>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="images"?(o(),r("div",tt,[t[98]||(t[98]=c('<h4 class="section-title" data-v-cf83ded4><i class="bi bi-images me-2 text-primary" data-v-cf83ded4></i>Images in Templates</h4><p class="text-muted" data-v-cf83ded4>Upload images to the gallery and reference them in your report templates using standard HTML <code data-v-cf83ded4>&lt;img&gt;</code> tags.</p><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-lightning me-2 text-warning" data-v-cf83ded4></i>Quick start</div><div class="card-body" data-v-cf83ded4><ol class="mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Go to <strong data-v-cf83ded4>Image Gallery</strong> (make sure you have an active project).</li><li class="mb-2" data-v-cf83ded4>Upload an image — drag &amp; drop or click <strong data-v-cf83ded4>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li><li class="mb-2" data-v-cf83ded4>Click the <i class="bi bi-link-45deg" data-v-cf83ded4></i> button on the image card to copy its <code data-v-cf83ded4>img:UUID</code> reference.</li><li data-v-cf83ded4>Paste it into an <code data-v-cf83ded4>&lt;img&gt;</code> tag in your template: <code data-v-cf83ded4>&lt;img src=&quot;img:IMAGE_ID&quot; alt=&quot;…&quot; /&gt;</code></li></ol></div></div>',3)),d("div",et,[t[97]||(t[97]=d("div",{class:"pattern-header pattern-1"},"Using images in templates",-1)),d("div",at,[t[96]||(t[96]=d("p",{class:"small text-muted mb-3"},[e("Use the image URL directly in an "),d("code",null,"<img>"),e(" tag. You can also use just the path (without the domain) since the report renders on the same origin.")],-1)),d("div",st,[t[93]||(t[93]=d("div",{class:"step-label"},"Basic image",-1)),d("pre",lt,a(l.image_basic),1)]),d("div",it,[t[94]||(t[94]=d("div",{class:"step-label"},"Logo in a report header",-1)),d("pre",rt,a(l.image_header),1)]),d("div",ot,[t[95]||(t[95]=d("div",{class:"step-label"},"Sized and styled",-1)),d("pre",ct,a(l.image_styled),1)])])]),t[99]||(t[99]=c('<div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-cf83ded4></i>Limitations</div><div class="card-body" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Works</th><th data-v-cf83ded4>Does not work</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>&lt;img src=&quot;img:IMAGE_ID&quot;&gt;</code></td><td data-v-cf83ded4><code data-v-cf83ded4>background-image: url(/api/v1/images/ID/data)</code></td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Standard <code data-v-cf83ded4>&lt;img&gt;</code> tags with inline styles</td><td data-v-cf83ded4>CSS <code data-v-cf83ded4>url()</code> references to gallery images (blocked by sanitizer)</td></tr></tbody></table><p class="small text-muted mt-2 mb-0" data-v-cf83ded4> The template CSS sanitizer strips non-<code data-v-cf83ded4>data:</code> URLs in stylesheets for security. Use <code data-v-cf83ded4>&lt;img&gt;</code> tags instead of CSS background images. </p></div></div><div class="card" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-info-circle me-2 text-info" data-v-cf83ded4></i>Tips</div><div class="card-body" data-v-cf83ded4><ul class="small mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Each project can hold up to <strong data-v-cf83ded4>20 images</strong>, each up to <strong data-v-cf83ded4>2 MB</strong>.</li><li class="mb-2" data-v-cf83ded4>Images are served with a 24-hour browser cache header, so they load quickly in previews.</li><li class="mb-2" data-v-cf83ded4>Use the <strong data-v-cf83ded4>Rename</strong> button to give images descriptive names for easy identification.</li><li data-v-cf83ded4>For logos and icons, <strong data-v-cf83ded4>SVG</strong> or <strong data-v-cf83ded4>WebP</strong> formats give the best quality-to-size ratio.</li></ul></div></div>',2))])):n("",!0),i.value==="markdown"?(o(),r("div",nt,[t[115]||(t[115]=c('<h4 class="section-title" data-v-cf83ded4><i class="bi bi-markdown me-2 text-primary" data-v-cf83ded4></i>Markdown Templates</h4><p class="text-muted" data-v-cf83ded4>Markdown templates let you write reports in GitHub Flavoured Markdown (GFM) combined with Mustache syntax. The editor switches to a Markdown language mode, and both the live preview and server-side renders parse the Markdown before display.</p><div class="row g-4 mb-4" data-v-cf83ded4><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-check-circle me-2 text-success" data-v-cf83ded4></i>When to use Markdown</div><div class="card-body" data-v-cf83ded4><ul class="small mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Text-heavy reports — summaries, memos, executive briefings</li><li class="mb-2" data-v-cf83ded4>Simple tables from query data without custom styling</li><li class="mb-2" data-v-cf83ded4>Reports where you want to write content quickly without HTML boilerplate</li><li data-v-cf83ded4>Situations where the AI assistant&#39;s output is primarily prose</li></ul></div></div></div><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-x-circle me-2 text-danger" data-v-cf83ded4></i>When to use HTML instead</div><div class="card-body" data-v-cf83ded4><ul class="small mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Multi-column layouts with Bootstrap grid</li><li class="mb-2" data-v-cf83ded4>Precise per-page styling with custom CSS</li><li class="mb-2" data-v-cf83ded4>KPI tiles or complex badge styling requiring custom CSS</li><li data-v-cf83ded4>Reports that require <code data-v-cf83ded4>.report-page</code> divs with controlled page breaks</li></ul></div></div></div></div>',3)),d("div",vt,[t[106]||(t[106]=d("div",{class:"card-header"},[d("i",{class:"bi bi-braces me-2"}),e("Mustache works the same way")],-1)),d("div",pt,[d("p",ut,[t[100]||(t[100]=e("All Mustache syntax — ",-1)),d("code",null,a(s.variable),1),t[101]||(t[101]=e(", ",-1)),d("code",null,a(s.section),1),t[102]||(t[102]=e(", ",-1)),d("code",null,a(s.inverted),1),t[103]||(t[103]=e(", dot notation — is evaluated first, then the result is parsed as Markdown. The ",-1)),d("code",null,a(s.rows_open),1),t[104]||(t[104]=e(" / ",-1)),d("code",null,a(s.rows_close),1),t[105]||(t[105]=e(" pattern still applies.",-1))]),d("pre",mt,a(l.markdown_basic),1)])]),d("div",ft,[t[111]||(t[111]=d("div",{class:"card-header"},[d("i",{class:"bi bi-table me-2"}),e("GFM tables with dynamic rows")],-1)),d("div",bt,[d("p",ht,[t[107]||(t[107]=e("Place the ",-1)),d("code",null,a(s.rows_open),1),t[108]||(t[108]=e(" loop inside the table body. Each iteration appends a row. Note: the closing ",-1)),d("code",null,a(s.rows_close),1),t[109]||(t[109]=e(" must sit on its own line.",-1))]),d("pre",gt,a(l.markdown_table),1),t[110]||(t[110]=d("div",{class:"alert alert-info mt-3 mb-0 py-2"},[d("i",{class:"bi bi-info-circle me-2"}),e(" Do not put blank lines between the pipe rows — GFM interprets a blank line as the end of the table. ")],-1))])]),t[116]||(t[116]=c('<div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-file-break me-2" data-v-cf83ded4></i>Page breaks</div><div class="card-body" data-v-cf83ded4><p class="small text-muted mb-2" data-v-cf83ded4>Inline HTML is allowed inside Markdown templates. Use a div with <code data-v-cf83ded4>page-break-after</code> to force a new page in PDF exports and print:</p><pre class="code-block" data-v-cf83ded4>&lt;div style=&quot;page-break-after: always&quot;&gt;&lt;/div&gt;</pre></div></div>',1)),d("div",yt,[t[114]||(t[114]=d("div",{class:"card-header"},[d("i",{class:"bi bi-bar-chart me-2"}),e("Charts in Markdown templates")],-1)),d("div",wt,[t[112]||(t[112]=d("p",{class:"small text-muted mb-3"},[e("Chart divs work inside Markdown templates via inline HTML passthrough. Paste a "),d("code",null,"report-bar-chart"),e(" or "),d("code",null,"report-pie-chart"),e(" div directly into your template — Mustache is evaluated first, then the chart is rendered as inline SVG before display.")],-1)),d("pre",_t,a(l.markdown_chart),1),t[113]||(t[113]=d("div",{class:"alert alert-success mt-3 mb-0 py-2"},[d("i",{class:"bi bi-check-circle me-2"}),e(" Charts render identically in browser preview, PDF export, and scheduled email delivery — no extra configuration required. ")],-1))])]),t[117]||(t[117]=c('<div class="card" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-list-check me-2" data-v-cf83ded4></i>Supported Markdown features</div><div class="card-body p-0" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Syntax</th><th data-v-cf83ded4>Output</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4># Heading</code> / <code data-v-cf83ded4>## H2</code> / <code data-v-cf83ded4>### H3</code></td><td data-v-cf83ded4>Heading elements</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>**bold**</code> / <code data-v-cf83ded4>*italic*</code></td><td data-v-cf83ded4>Strong / emphasis</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>- item</code> / <code data-v-cf83ded4>1. item</code></td><td data-v-cf83ded4>Unordered / ordered lists</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>- [x] done</code> / <code data-v-cf83ded4>- [ ] todo</code></td><td data-v-cf83ded4>Task list checkboxes</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>&gt; blockquote</code></td><td data-v-cf83ded4>Callout / pull-quote block</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>`code`</code> / <code data-v-cf83ded4>```block```</code></td><td data-v-cf83ded4>Inline / fenced code</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>| Col | Col |</code> + header separator</td><td data-v-cf83ded4>GFM table</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>---</code></td><td data-v-cf83ded4>Horizontal rule</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4>Inline HTML</td><td data-v-cf83ded4>Passed through (page breaks, images, charts, etc.)</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="scheduling"?(o(),r("div",kt,[...t[118]||(t[118]=[c('<h4 class="section-title" data-v-cf83ded4><i class="bi bi-clock-history me-2 text-primary" data-v-cf83ded4></i>Scheduling</h4><p class="text-muted" data-v-cf83ded4>Schedules automate report rendering on a recurring basis using standard cron expressions. The app&#39;s service principal executes the query and renders the template server-side — no user session is required.</p><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-lightning me-2 text-warning" data-v-cf83ded4></i>Quick start</div><div class="card-body" data-v-cf83ded4><ol class="mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Make sure the app&#39;s service principal has <code data-v-cf83ded4>SELECT</code> privilege on every Unity Catalog table used by the report&#39;s data structure.</li><li class="mb-2" data-v-cf83ded4>Open <strong data-v-cf83ded4>Schedules</strong> from the sidebar (an active project must be selected).</li><li class="mb-2" data-v-cf83ded4>Click <strong data-v-cf83ded4>New Schedule</strong>, choose a data structure and template, set a frequency, and click <strong data-v-cf83ded4>Create Schedule</strong>.</li><li class="mb-2" data-v-cf83ded4>The schedule is registered immediately. Use the <i class="bi bi-play-fill" data-v-cf83ded4></i> button to trigger a test run without waiting for the next cron tick.</li><li data-v-cf83ded4>Switch to the <strong data-v-cf83ded4>Execution History</strong> tab and click <i class="bi bi-list-check" data-v-cf83ded4></i> on any schedule to review past runs and error messages.</li></ol></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-cf83ded4></i>Service principal requirement</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4> Scheduled executions run in the background without a user session. The app queries Databricks using the <strong data-v-cf83ded4>service principal credentials</strong> configured in the environment (<code data-v-cf83ded4>DATABRICKS_CLIENT_ID</code> / <code data-v-cf83ded4>DATABRICKS_CLIENT_SECRET</code> or <code data-v-cf83ded4>DATABRICKS_TOKEN</code>). </p><p class="small mb-0 text-danger fw-semibold" data-v-cf83ded4> If the service principal does not have <code data-v-cf83ded4>SELECT</code> on the relevant UC tables, every scheduled execution will fail with a permissions error. </p></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-calendar-week me-2" data-v-cf83ded4></i>Cron expression format</div><div class="card-body" data-v-cf83ded4><p class="small text-muted mb-3" data-v-cf83ded4>Schedules use standard 5-field cron syntax: <code data-v-cf83ded4>minute hour day month day_of_week</code>.</p><table class="table table-sm mb-3" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Expression</th><th data-v-cf83ded4>Meaning</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>0 9 * * *</code></td><td data-v-cf83ded4>Every day at 09:00</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>0 9 * * 1-5</code></td><td data-v-cf83ded4>Weekdays (Mon–Fri) at 09:00</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>0 8 * * 1</code></td><td data-v-cf83ded4>Every Monday at 08:00</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>0 6 1 * *</code></td><td data-v-cf83ded4>1st of every month at 06:00</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>*/15 * * * *</code></td><td data-v-cf83ded4>Every 15 minutes</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><code data-v-cf83ded4>30 17 * * 5</code></td><td data-v-cf83ded4>Every Friday at 17:30</td></tr></tbody></table><p class="small text-muted mb-0" data-v-cf83ded4> The schedule builder&#39;s <strong data-v-cf83ded4>Simple</strong> mode generates a cron expression for you. Switch to <strong data-v-cf83ded4>Cron</strong> mode to enter one manually. </p></div></div><div class="card mb-4" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-list-check me-2" data-v-cf83ded4></i>Execution statuses</div><div class="card-body p-0" data-v-cf83ded4><table class="table table-sm mb-0" data-v-cf83ded4><thead class="table-dark" data-v-cf83ded4><tr data-v-cf83ded4><th data-v-cf83ded4>Status</th><th data-v-cf83ded4>Meaning</th></tr></thead><tbody data-v-cf83ded4><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge bg-primary" data-v-cf83ded4>running</span></td><td data-v-cf83ded4>The execution is in progress. The history panel auto-refreshes every 10 seconds while a run is active.</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge bg-success" data-v-cf83ded4>success</span></td><td data-v-cf83ded4>The report rendered without error.</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge bg-danger" data-v-cf83ded4>failed</span></td><td data-v-cf83ded4>The run failed — check the <strong data-v-cf83ded4>Error</strong> column for details (missing UC privilege, bad Mustache syntax, warehouse timeout, etc.).</td></tr><tr data-v-cf83ded4><td data-v-cf83ded4><span class="badge bg-secondary" data-v-cf83ded4>pending</span></td><td data-v-cf83ded4>Queued but not yet started.</td></tr></tbody></table></div></div><div class="row g-4 mb-4" data-v-cf83ded4><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-pencil me-2 text-primary" data-v-cf83ded4></i>Editing a schedule</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>Click the <i class="bi bi-pencil" data-v-cf83ded4></i> button to change a schedule&#39;s <strong data-v-cf83ded4>name</strong>, <strong data-v-cf83ded4>cron expression</strong>, or <strong data-v-cf83ded4>active</strong> status.</p><p class="small mb-2" data-v-cf83ded4>The linked structure and template cannot be changed after creation — delete and recreate the schedule if you need a different template.</p><p class="small mb-0 text-muted" data-v-cf83ded4>Saving a cron change re-registers the APScheduler job immediately.</p></div></div></div><div class="col-md-6" data-v-cf83ded4><div class="card h-100" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-toggle-on me-2 text-success" data-v-cf83ded4></i>Active vs Inactive</div><div class="card-body" data-v-cf83ded4><p class="small mb-2" data-v-cf83ded4>Inactive schedules are not registered with the scheduler — they will not fire automatically.</p><p class="small mb-2" data-v-cf83ded4>Toggling a schedule back to <strong data-v-cf83ded4>Active</strong> immediately re-registers the cron job with no further action required.</p><p class="small mb-0 text-muted" data-v-cf83ded4>The manual trigger button (<i class="bi bi-play-fill" data-v-cf83ded4></i>) works regardless of the active flag.</p></div></div></div></div><div class="card" data-v-cf83ded4><div class="card-header" data-v-cf83ded4><i class="bi bi-info-circle me-2 text-info" data-v-cf83ded4></i>Tips &amp; limitations</div><div class="card-body" data-v-cf83ded4><ul class="small mb-0" data-v-cf83ded4><li class="mb-2" data-v-cf83ded4>Schedules are scoped to a project — select the project in the sidebar before navigating to the Schedules page.</li><li class="mb-2" data-v-cf83ded4>The scheduler runs in the same process as the FastAPI back-end. If the app restarts, all active schedules are automatically re-registered from the database on startup.</li><li class="mb-2" data-v-cf83ded4>Execution history is paginated to the last 50 runs by default. Use the offset/limit query parameters on the API if you need older entries.</li><li class="mb-2" data-v-cf83ded4>Only the project owner and shared members can create or modify schedules. The <code data-v-cf83ded4>check_schedule_project_access</code> guard applies the same access + lock rules as structures and templates.</li><li data-v-cf83ded4>Scheduled renders use a <strong data-v-cf83ded4>10,000 row limit</strong> on the SQL query — the same as a full PDF export.</li></ul></div></div>',8)])])):n("",!0)])])]))}}),Rt=g(xt,[["__scopeId","data-v-cf83ded4"]]);export{Rt as default};
