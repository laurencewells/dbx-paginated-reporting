import{d as m,c as r,a,b as e,F as u,v as b,e as c,y as n,x as s,D as g,o,w as v,_ as h}from"./index-VQMw-gLd.js";const y={class:"guide-view"},w={class:"row g-4"},_={class:"col-md-3"},k={class:"card sticky-top",style:{top:"calc(var(--pr-navbar-height) + 1rem)"}},x={class:"card-body p-2"},S=["onClick"],T={class:"col-md-9"},C={key:0},A={key:1},R={class:"card mb-4"},M={class:"card-body p-0"},j={class:"table table-sm mb-0"},E={class:"syntax-tag"},L={class:"syntax-tag"},P={class:"syntax-tag"},q={class:"syntax-tag"},I={class:"syntax-tag"},U={class:"syntax-tag"},D={class:"alert alert-warning"},H={class:"ms-1"},F={class:"card"},N={class:"card-body"},G={class:"code-block"},O={class:"mb-0 small text-muted mt-2"},Q={key:2},V={class:"pattern-step"},B={class:"code-block"},Y={class:"pattern-step"},W={class:"code-block"},z={class:"pattern-step"},K={class:"code-block"},J={class:"alert alert-info"},$={key:3},X={class:"pattern-step"},Z={class:"code-block"},aa={class:"pattern-step"},ta={class:"code-block"},ea={class:"pattern-step"},sa={class:"row g-3"},da={class:"col-md-6"},la={class:"approach-card"},ia={class:"code-block"},ra={class:"small text-muted mt-2 mb-0"},oa={class:"col-md-6"},na={class:"approach-card"},ca={class:"code-block"},fa={key:4},va={class:"pattern-step"},pa={class:"code-block"},ma={class:"pattern-step"},ua={class:"code-block"},ba={class:"pattern-step"},ga={class:"code-block"},ha={class:"alert alert-info"},ya={key:5},wa={class:"pattern-card mb-4"},_a={class:"card-body"},ka={class:"code-block"},xa={class:"pattern-card mb-4"},Sa={class:"card-body"},Ta={class:"code-block"},Ca={class:"pattern-card mb-4"},Aa={class:"card-body"},Ra={class:"pattern-step"},Ma={class:"code-block"},ja={class:"pattern-step"},Ea={class:"code-block"},La={class:"pattern-step"},Pa={class:"code-block"},qa={key:6},Ia={class:"pattern-card mb-4"},Ua={class:"card-body"},Da={class:"pattern-step"},Ha={class:"code-block"},Fa={class:"pattern-step"},Na={class:"code-block"},Ga={class:"alert alert-success mb-0"},Oa={class:"pattern-card mb-4"},Qa={class:"card-body"},Va={class:"small text-muted mb-3"},Ba={class:"pattern-step"},Ya={class:"code-block"},Wa={class:"pattern-step"},za={class:"code-block"},Ka={key:7},Ja={class:"pattern-card mb-4"},$a={class:"card-body"},Xa={class:"pattern-step"},Za={class:"code-block"},at={class:"pattern-step"},tt={class:"code-block"},et={class:"pattern-step"},st={class:"code-block"},dt={key:8},lt={class:"card mb-4"},it={class:"card-body"},rt={class:"small text-muted mb-3"},ot={class:"code-block"},nt={class:"card mb-4"},ct={class:"card-body"},ft={class:"small text-muted mb-3"},vt={class:"code-block"},pt={key:9},mt=m({__name:"GuideView",setup(ut){const i=g("projects"),p=[{id:"projects",label:"Projects",icon:"bi-folder2-open"},{id:"mustache",label:"Mustache Syntax",icon:"bi-braces"},{id:"flat-table",label:"Flat Table",icon:"bi-table"},{id:"struct",label:"Struct Fields",icon:"bi-braces-asterisk"},{id:"array-struct",label:"Array of Structs",icon:"bi-list-nested"},{id:"chart-struct",label:"Charts from Structs",icon:"bi-bar-chart"},{id:"conditional-styles",label:"Conditional Styles",icon:"bi-palette"},{id:"images",label:"Images",icon:"bi-images"},{id:"markdown",label:"Markdown Templates",icon:"bi-markdown"},{id:"scheduling",label:"Scheduling",icon:"bi-clock-history"}],d={variable:"{{field}}",triple:"{{{field}}}",section:"{{#section}}...{{/section}}",inverted:"{{^section}}...{{/section}}",dot:"{{.}}",comment:"{{! comment }}",ex_field:"{{cluster_name}}",ex_dot_loop:"{{#tags}}{{.}}{{/tags}}",ex_comment:"{{! TODO: add chart }}",rows_open:"{{#rows}}",rows_close:"{{/rows}}",rows_wrong:"{{/#}}",delete_check:"{{^delete_time}}Active{{/delete_time}}",index:"{{_index}}",total:"{{_total}}",address_open:"{{#address}}",cond_class_example:"status-{{approval_status}}"},l={dataShape:`{
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
{{/rows}}`,image_basic:'<img src="/api/v1/images/IMAGE_ID/data" alt="Description" />',image_header:`<div class="report-page">
  <div class="report-page-header d-flex align-items-center gap-3">
    <img src="/api/v1/images/IMAGE_ID/data"
         alt="Company Logo"
         style="height: 48px;" />
    <h1 class="mb-0">Monthly Report</h1>
  </div>

  <div class="report-page-content">
    <!-- report content here -->
  </div>
</div>`,image_styled:`<img src="/api/v1/images/IMAGE_ID/data"
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
{{/rows}}`};return(bt,t)=>(o(),r("div",y,[t[112]||(t[112]=a("div",{class:"guide-header mb-4"},[a("h2",{class:"mb-1"},[a("i",{class:"bi bi-book text-primary me-2"}),e(" Template Guide ")]),a("p",{class:"text-muted mb-0"}," How to structure your data and write Mustache templates for reports ")],-1)),a("div",w,[a("div",_,[a("div",k,[a("div",x,[(o(),r(u,null,b(p,f=>a("button",{key:f.id,class:v(["guide-nav-btn",{active:i.value===f.id}]),onClick:gt=>i.value=f.id},[a("i",{class:v(["bi",f.icon,"me-2"])},null,2),e(" "+s(f.label),1)],10,S)),64))])])]),a("div",T,[i.value==="projects"?(o(),r("div",C,[...t[0]||(t[0]=[c('<h4 class="section-title" data-v-1f12fa2e><i class="bi bi-folder2-open me-2 text-primary" data-v-1f12fa2e></i>Projects</h4><p class="text-muted" data-v-1f12fa2e>Projects group related data structures and templates together, making it easy to organise, share, and lock your work.</p><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-lightning me-2 text-warning" data-v-1f12fa2e></i>Getting started</div><div class="card-body" data-v-1f12fa2e><ol class="mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Navigate to <strong data-v-1f12fa2e>Projects</strong> and click <strong data-v-1f12fa2e>New Project</strong>.</li><li class="mb-2" data-v-1f12fa2e>Give it a name (e.g. &quot;Q1 Sales Reports&quot;) and click <strong data-v-1f12fa2e>Create</strong>.</li><li class="mb-2" data-v-1f12fa2e>Click <strong data-v-1f12fa2e>Open</strong> to set it as your active project — you&#39;ll see a banner in the sidebar.</li><li class="mb-2" data-v-1f12fa2e>Now go to <strong data-v-1f12fa2e>Data Structures</strong> — any structures you create will automatically belong to this project.</li><li data-v-1f12fa2e>Create templates linked to those structures, then use the <strong data-v-1f12fa2e>Export</strong> button in the Template Editor to preview and export PDF.</li></ol></div></div><div class="row g-4 mb-4" data-v-1f12fa2e><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-diagram-3 me-2 text-primary" data-v-1f12fa2e></i>How structures are linked</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>When a project is active, new structures are automatically associated with it via a <code data-v-1f12fa2e>project_id</code> field.</p><p class="small mb-2" data-v-1f12fa2e>The Data Structures and Template Editor pages filter their lists to show only items belonging to the active project.</p><p class="small mb-0 text-muted" data-v-1f12fa2e>Clear the project filter (click the <i class="bi bi-x-lg" data-v-1f12fa2e></i> in the sidebar banner) to see all structures across all projects.</p></div></div></div><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-file-code me-2 text-success" data-v-1f12fa2e></i>How templates are linked</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>Templates don&#39;t have a direct project link — they&#39;re associated through their <strong data-v-1f12fa2e>structure</strong>.</p><p class="small mb-0" data-v-1f12fa2e>When filtering by project, the app shows templates whose linked structure belongs to the active project.</p></div></div></div></div><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-lock me-2 text-warning" data-v-1f12fa2e></i>Locking</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>Only the project <strong data-v-1f12fa2e>owner</strong> can lock or unlock a project.</p><p class="small mb-2" data-v-1f12fa2e>When a project is <strong data-v-1f12fa2e>locked</strong>, all create, update, and delete operations on its structures and templates are blocked with a <code data-v-1f12fa2e>423 Locked</code> response.</p><p class="small mb-0 text-muted" data-v-1f12fa2e>This is useful when a report set is finalised and you want to prevent accidental edits.</p></div></div><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-people me-2 text-info" data-v-1f12fa2e></i>Sharing</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>Share a project with colleagues by entering their email address on the project detail panel.</p><p class="small mb-2" data-v-1f12fa2e>Shared users can <strong data-v-1f12fa2e>view</strong> and <strong data-v-1f12fa2e>edit</strong> structures and templates in the project (unless it&#39;s locked).</p><p class="small mb-2" data-v-1f12fa2e>Only the project <strong data-v-1f12fa2e>owner</strong> can:</p><ul class="small mb-0" data-v-1f12fa2e><li data-v-1f12fa2e>Lock / unlock the project</li><li data-v-1f12fa2e>Add or remove shares</li><li data-v-1f12fa2e>Delete the project</li></ul></div></div><div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-table me-2" data-v-1f12fa2e></i>Permission summary</div><div class="card-body p-0" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Action</th><th data-v-1f12fa2e>Owner</th><th data-v-1f12fa2e>Shared user</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e>View structures &amp; templates</td><td class="text-success" data-v-1f12fa2e>Yes</td><td class="text-success" data-v-1f12fa2e>Yes</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Create / edit / delete structures &amp; templates</td><td class="text-success" data-v-1f12fa2e>Yes (if unlocked)</td><td class="text-success" data-v-1f12fa2e>Yes (if unlocked)</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Lock / unlock project</td><td class="text-success" data-v-1f12fa2e>Yes</td><td class="text-danger" data-v-1f12fa2e>No</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Share / unshare project</td><td class="text-success" data-v-1f12fa2e>Yes</td><td class="text-danger" data-v-1f12fa2e>No</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Delete project</td><td class="text-success" data-v-1f12fa2e>Yes</td><td class="text-danger" data-v-1f12fa2e>No</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Rename project</td><td class="text-success" data-v-1f12fa2e>Yes</td><td class="text-danger" data-v-1f12fa2e>No</td></tr></tbody></table></div></div>',7)])])):n("",!0),i.value==="mustache"?(o(),r("div",A,[t[21]||(t[21]=a("h4",{class:"section-title"},[a("i",{class:"bi bi-braces me-2 text-primary"}),e("Mustache Syntax Reference")],-1)),t[22]||(t[22]=a("p",{class:"text-muted"},[e("Mustache is a logic-less templating language. All data comes from the "),a("code",null,"rows"),e(" array returned by your SQL query.")],-1)),a("div",R,[a("div",M,[a("table",j,[t[10]||(t[10]=a("thead",{class:"table-dark"},[a("tr",null,[a("th",null,"Syntax"),a("th",null,"Purpose"),a("th",null,"Example")])],-1)),a("tbody",null,[a("tr",null,[a("td",null,[a("code",E,s(d.variable),1)]),t[1]||(t[1]=a("td",null,"Render a value (HTML-escaped)",-1)),a("td",null,[a("code",null,s(d.ex_field),1)])]),a("tr",null,[a("td",null,[a("code",L,s(d.triple),1)]),t[2]||(t[2]=a("td",null,"Render raw HTML (unescaped)",-1)),a("td",null,[a("code",null,s(d.triple),1)])]),a("tr",null,[a("td",null,[a("code",P,s(d.section),1)]),t[3]||(t[3]=a("td",null,[e("Iterate array "),a("strong",null,"or"),e(" render if truthy")],-1)),a("td",null,[a("code",null,s(d.rows_open)+"..."+s(d.rows_close),1)])]),a("tr",null,[a("td",null,[a("code",q,s(d.inverted),1)]),t[4]||(t[4]=a("td",null,"Render if falsy or empty",-1)),a("td",null,[a("code",null,s(d.delete_check),1)])]),a("tr",null,[a("td",null,[a("code",I,s(d.dot),1)]),t[8]||(t[8]=a("td",null,[e("Current item in a "),a("em",null,"scalar"),e(" list only")],-1)),a("td",null,[a("code",null,s(d.ex_dot_loop),1),t[5]||(t[5]=e(" (tags is ",-1)),t[6]||(t[6]=a("code",null,'["a","b"]',-1)),t[7]||(t[7]=e(")",-1))])]),a("tr",null,[a("td",null,[a("code",U,s(d.comment),1)]),t[9]||(t[9]=a("td",null,"Comment — not rendered",-1)),a("td",null,[a("code",null,s(d.ex_comment),1)])])])])])]),a("div",D,[t[11]||(t[11]=a("i",{class:"bi bi-exclamation-triangle-fill me-2"},null,-1)),t[12]||(t[12]=a("strong",null,"Closing tags must always match the opening name exactly.",-1)),a("code",H,s(d.rows_open),1),t[13]||(t[13]=e(" closes with ",-1)),a("code",null,s(d.rows_close),1),t[14]||(t[14]=e(" — never ",-1)),a("code",null,s(d.rows_wrong),1),t[15]||(t[15]=e(". ",-1))]),a("div",F,[t[20]||(t[20]=a("div",{class:"card-header"},[a("i",{class:"bi bi-lightbulb me-2 text-warning"}),e("Key rule — your data is always "),a("code",null,"rows")],-1)),a("div",N,[t[19]||(t[19]=a("p",{class:"mb-2"},[e("Every query returns a single top-level key "),a("code",null,"rows"),e(", which is a list of objects:")],-1)),a("pre",G,s(l.dataShape),1),a("p",O,[t[16]||(t[16]=e("Each row also receives ",-1)),a("code",null,s(d.index),1),t[17]||(t[17]=e(" (1-based position) and ",-1)),a("code",null,s(d.total),1),t[18]||(t[18]=e(" (total row count) automatically.",-1))])])])])):n("",!0),i.value==="flat-table"?(o(),r("div",Q,[t[30]||(t[30]=a("h4",{class:"section-title"},[a("i",{class:"bi bi-table me-2 text-primary"}),e("Flat Table Report")],-1)),t[31]||(t[31]=a("p",{class:"text-muted"},"The most common pattern — scalar columns from a Unity Catalog table rendered as a report table.",-1)),a("div",V,[t[23]||(t[23]=a("div",{class:"step-label"},"1 · Unity Catalog Table",-1)),a("pre",B,s(l.flatTable_sql),1)]),a("div",Y,[t[24]||(t[24]=a("div",{class:"step-label"},"2 · Data Shape delivered to template",-1)),a("pre",W,s(l.flatTable_data),1)]),a("div",z,[t[25]||(t[25]=a("div",{class:"step-label"},"3 · Mustache Template",-1)),a("pre",K,s(l.flatTable_template),1)]),a("div",J,[t[26]||(t[26]=a("i",{class:"bi bi-info-circle me-2"},null,-1)),t[27]||(t[27]=a("strong",null,"Null / empty check:",-1)),t[28]||(t[28]=e(" use ",-1)),a("code",null,s(d.inverted),1),t[29]||(t[29]=e(" to render content when a field is null, false, or empty — no logic needed. ",-1))])])):n("",!0),i.value==="struct"?(o(),r("div",$,[t[39]||(t[39]=a("h4",{class:"section-title"},[a("i",{class:"bi bi-braces-asterisk me-2 text-primary"}),e("Struct Fields")],-1)),t[40]||(t[40]=a("p",{class:"text-muted"},[e("When a column is "),a("code",null,"STRUCT<...>"),e(", Mustache can push it as a context or access it with dot notation.")],-1)),a("div",X,[t[32]||(t[32]=a("div",{class:"step-label"},"1 · Unity Catalog Table with a STRUCT column",-1)),a("pre",Z,s(l.struct_sql),1)]),a("div",aa,[t[33]||(t[33]=a("div",{class:"step-label"},"2 · Data Shape",-1)),a("pre",ta,s(l.struct_data),1)]),a("div",ea,[t[38]||(t[38]=a("div",{class:"step-label"},"3 · Template — two equivalent approaches",-1)),a("div",sa,[a("div",da,[a("div",la,[t[35]||(t[35]=a("div",{class:"approach-label"},"Context push (recommended)",-1)),a("pre",ia,s(l.struct_context),1),a("p",ra,[a("code",null,s(d.address_open),1),t[34]||(t[34]=e(" pushes the struct as context — child fields are then in scope directly.",-1))])])]),a("div",oa,[a("div",na,[t[36]||(t[36]=a("div",{class:"approach-label"},"Dot notation",-1)),a("pre",ca,s(l.struct_dot),1),t[37]||(t[37]=a("p",{class:"small text-muted mt-2 mb-0"},"Dot notation accesses nested fields without a context push — useful for one or two fields.",-1))])])])])])):n("",!0),i.value==="array-struct"?(o(),r("div",fa,[t[52]||(t[52]=a("h4",{class:"section-title"},[a("i",{class:"bi bi-list-nested me-2 text-primary"}),e("Array of Structs")],-1)),t[53]||(t[53]=a("p",{class:"text-muted"},[e("When a column is "),a("code",null,"ARRAY<STRUCT<...>>"),e(", iterate the outer "),a("code",null,"rows"),e(" first, then the nested array inside.")],-1)),a("div",va,[t[41]||(t[41]=a("div",{class:"step-label"},"1 · Unity Catalog Table with ARRAY<STRUCT>",-1)),a("pre",pa,s(l.array_sql),1)]),a("div",ma,[t[42]||(t[42]=a("div",{class:"step-label"},"2 · Data Shape",-1)),a("pre",ua,s(l.array_data),1)]),a("div",ba,[t[43]||(t[43]=a("div",{class:"step-label"},"3 · Template — nested iteration",-1)),a("pre",ga,s(l.array_template),1)]),a("div",ha,[t[44]||(t[44]=a("i",{class:"bi bi-info-circle me-2"},null,-1)),t[45]||(t[45]=a("strong",null,"One page per order:",-1)),t[46]||(t[46]=e(" the outer ",-1)),a("code",null,s(d.rows_open),1),t[47]||(t[47]=e(" wraps a ",-1)),t[48]||(t[48]=a("code",null,".report-page",-1)),t[49]||(t[49]=e(" div, so each order gets its own page. ",-1)),a("code",null,s(d.index),1),t[50]||(t[50]=e(" and ",-1)),a("code",null,s(d.total),1),t[51]||(t[51]=e(" are available on each row. ",-1))])])):n("",!0),i.value==="chart-struct"?(o(),r("div",ya,[t[65]||(t[65]=c('<h4 class="section-title" data-v-1f12fa2e><i class="bi bi-bar-chart me-2 text-primary" data-v-1f12fa2e></i>Charts from Struct Columns</h4><div class="alert alert-success py-2 mb-3" data-v-1f12fa2e><i class="bi bi-check-circle me-2" data-v-1f12fa2e></i>Charts render as <strong data-v-1f12fa2e>inline SVG</strong> — they display identically in the browser preview, PDF export, and email delivery. No JavaScript required at render time. </div><p class="text-muted" data-v-1f12fa2e>Charts read comma-separated strings from <code data-v-1f12fa2e>data-labels</code> and <code data-v-1f12fa2e>data-values</code> attributes. There are three ways to feed data in.</p>',3)),a("div",wa,[t[56]||(t[56]=a("div",{class:"pattern-header pattern-1"},[e("Pattern 1 — Aggregate the main "),a("code",null,"rows"),e(" array (simplest)")],-1)),a("div",_a,[t[54]||(t[54]=a("p",{class:"small text-muted mb-3"},"Use when each row already represents one data point you want to plot.",-1)),a("pre",ka,s(l.chart1_template),1),t[55]||(t[55]=a("p",{class:"small text-muted mt-2 mb-0"},[e("Mustache renders the loops into: "),a("code",null,'data-labels="EMEA,APAC,AMER,"'),e(" — trailing commas are ignored by the parser.")],-1))])]),a("div",xa,[t[58]||(t[58]=a("div",{class:"pattern-header pattern-2"},"Pattern 2 — Pre-aggregated scalar columns",-1)),a("div",Sa,[t[57]||(t[57]=a("p",{class:"small text-muted mb-3"},"SQL returns a single summary row with named columns — good for a KPI pie chart on a cover page.",-1)),a("pre",Ta,s(l.chart2_template),1)])]),a("div",Ca,[t[64]||(t[64]=a("div",{class:"pattern-header pattern-3"},"Pattern 3 — ARRAY<STRUCT> chart column (self-contained)",-1)),a("div",Aa,[t[62]||(t[62]=a("p",{class:"small text-muted mb-3"},"The SQL pre-aggregates chart data into an array column alongside row-level data. Each row carries its own independent chart dataset.",-1)),a("div",Ra,[t[59]||(t[59]=a("div",{class:"step-label"},"SQL",-1)),a("pre",Ma,s(l.chart3_sql),1)]),a("div",ja,[t[60]||(t[60]=a("div",{class:"step-label"},"Data Shape",-1)),a("pre",Ea,s(l.chart3_data),1)]),a("div",La,[t[61]||(t[61]=a("div",{class:"step-label"},"Template — one page per team, each with its own chart",-1)),a("pre",Pa,s(l.chart3_template),1)]),t[63]||(t[63]=a("div",{class:"alert alert-success mb-0"},[a("i",{class:"bi bi-check-circle-fill me-2"}),a("strong",null,"Why this pattern is powerful:"),e(" each team's chart is driven entirely by its own "),a("code",null,"spend_by_month"),e(" array — no global aggregation needed in the template. The SQL does the work, the template just renders it. ")],-1))])]),t[66]||(t[66]=c('<div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-table me-2" data-v-1f12fa2e></i>Pattern comparison</div><div class="card-body p-0" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Pattern</th><th data-v-1f12fa2e>SQL complexity</th><th data-v-1f12fa2e>Best for</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge pattern-badge-1" data-v-1f12fa2e>1 — Aggregate rows</span></td><td data-v-1f12fa2e>Low</td><td data-v-1f12fa2e>Single summary chart across all rows</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge pattern-badge-2" data-v-1f12fa2e>2 — Scalar columns</span></td><td data-v-1f12fa2e>Low–Medium</td><td data-v-1f12fa2e>Fixed labels, one summary row</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge pattern-badge-3" data-v-1f12fa2e>3 — Struct array</span></td><td data-v-1f12fa2e>Medium</td><td data-v-1f12fa2e>Per-row charts with different datasets on each page</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="conditional-styles"?(o(),r("div",qa,[t[87]||(t[87]=a("h4",{class:"section-title"},[a("i",{class:"bi bi-palette me-2 text-primary"}),e("Conditional Styles")],-1)),t[88]||(t[88]=a("p",{class:"text-muted"},"Mustache has no expression evaluator, but two clean patterns let you drive colours and layout from data values.",-1)),a("div",Ia,[t[80]||(t[80]=a("div",{class:"pattern-header pattern-1"},"Pattern 1 — CSS class from value (styling only, no SQL changes)",-1)),a("div",Ua,[t[79]||(t[79]=a("p",{class:"small text-muted mb-3"},[e(" Interpolate the field value directly into the class name. Add a "),a("code",null,"<style>"),e(" block at the top of your template with one rule per expected value. Best for badge colours, row highlights, or any purely visual difference. ")],-1)),a("div",Da,[t[67]||(t[67]=a("div",{class:"step-label"},"SQL — no changes needed",-1)),a("pre",Ha,s(l.conditional_sql_pattern1),1)]),a("div",Fa,[t[68]||(t[68]=a("div",{class:"step-label"},"Template",-1)),a("pre",Na,s(l.conditional_template_pattern1),1)]),a("div",Ga,[t[69]||(t[69]=a("i",{class:"bi bi-check-circle-fill me-2"},null,-1)),t[70]||(t[70]=a("strong",null,"How it works:",-1)),t[71]||(t[71]=e()),a("code",null,s(d.cond_class_example),1),t[72]||(t[72]=e(" renders as ",-1)),t[73]||(t[73]=a("code",null,"status-approved",-1)),t[74]||(t[74]=e(", ",-1)),t[75]||(t[75]=a("code",null,"status-pending",-1)),t[76]||(t[76]=e(", or ",-1)),t[77]||(t[77]=a("code",null,"status-rejected",-1)),t[78]||(t[78]=e(". Your CSS rules match on those exact class names. ",-1))])])]),a("div",Oa,[t[86]||(t[86]=a("div",{class:"pattern-header pattern-2"},"Pattern 2 — SQL boolean flags (show/hide entire blocks)",-1)),a("div",Qa,[a("p",Va,[t[81]||(t[81]=e(" Add computed boolean columns to your SQL query. Mustache sections (",-1)),a("code",null,s(d.section),1),t[82]||(t[82]=e(") render only when the value is truthy, giving you a full conditional block — not just a style change. ",-1))]),a("div",Ba,[t[83]||(t[83]=a("div",{class:"step-label"},"SQL — add boolean columns",-1)),a("pre",Ya,s(l.conditional_sql_pattern2),1)]),a("div",Wa,[t[84]||(t[84]=a("div",{class:"step-label"},"Template — conditional blocks",-1)),a("pre",za,s(l.conditional_template_pattern2),1)]),t[85]||(t[85]=a("div",{class:"alert alert-info mb-0"},[a("i",{class:"bi bi-info-circle me-2"}),a("strong",null,"When to use Pattern 2:"),e(" when you need to show different content, not just different colours — e.g. a rejection reason block that only appears for rejected suppliers. ")],-1))])]),t[89]||(t[89]=c('<div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-table me-2" data-v-1f12fa2e></i>Pattern comparison</div><div class="card-body p-0" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Pattern</th><th data-v-1f12fa2e>SQL change?</th><th data-v-1f12fa2e>Best for</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge pattern-badge-1" data-v-1f12fa2e>1 — CSS class from value</span></td><td data-v-1f12fa2e>None</td><td data-v-1f12fa2e>Badge colours, row highlights, status indicators</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge pattern-badge-2" data-v-1f12fa2e>2 — SQL boolean flags</span></td><td data-v-1f12fa2e>Add <code data-v-1f12fa2e>field = &#39;value&#39; AS is_x</code></td><td data-v-1f12fa2e>Conditional blocks, different content per status</td></tr></tbody></table></div></div>',1))])):n("",!0),i.value==="images"?(o(),r("div",Ka,[t[95]||(t[95]=c('<h4 class="section-title" data-v-1f12fa2e><i class="bi bi-images me-2 text-primary" data-v-1f12fa2e></i>Images in Templates</h4><p class="text-muted" data-v-1f12fa2e>Upload images to the gallery and reference them in your report templates using standard HTML <code data-v-1f12fa2e>&lt;img&gt;</code> tags.</p><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-lightning me-2 text-warning" data-v-1f12fa2e></i>Quick start</div><div class="card-body" data-v-1f12fa2e><ol class="mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Go to <strong data-v-1f12fa2e>Image Gallery</strong> (make sure you have an active project).</li><li class="mb-2" data-v-1f12fa2e>Upload an image — drag &amp; drop or click <strong data-v-1f12fa2e>Upload</strong>. Supported formats: JPEG, PNG, GIF, WebP, SVG (max 2 MB).</li><li class="mb-2" data-v-1f12fa2e>Click the <i class="bi bi-link-45deg" data-v-1f12fa2e></i> button on the image card to copy its URL.</li><li data-v-1f12fa2e>Paste the URL into an <code data-v-1f12fa2e>&lt;img&gt;</code> tag in your template.</li></ol></div></div>',3)),a("div",Ja,[t[94]||(t[94]=a("div",{class:"pattern-header pattern-1"},"Using images in templates",-1)),a("div",$a,[t[93]||(t[93]=a("p",{class:"small text-muted mb-3"},[e("Use the image URL directly in an "),a("code",null,"<img>"),e(" tag. You can also use just the path (without the domain) since the report renders on the same origin.")],-1)),a("div",Xa,[t[90]||(t[90]=a("div",{class:"step-label"},"Basic image",-1)),a("pre",Za,s(l.image_basic),1)]),a("div",at,[t[91]||(t[91]=a("div",{class:"step-label"},"Logo in a report header",-1)),a("pre",tt,s(l.image_header),1)]),a("div",et,[t[92]||(t[92]=a("div",{class:"step-label"},"Sized and styled",-1)),a("pre",st,s(l.image_styled),1)])])]),t[96]||(t[96]=c('<div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-1f12fa2e></i>Limitations</div><div class="card-body" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Works</th><th data-v-1f12fa2e>Does not work</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>&lt;img src=&quot;/api/v1/images/ID/data&quot;&gt;</code></td><td data-v-1f12fa2e><code data-v-1f12fa2e>background-image: url(/api/v1/images/ID/data)</code></td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Standard <code data-v-1f12fa2e>&lt;img&gt;</code> tags with inline styles</td><td data-v-1f12fa2e>CSS <code data-v-1f12fa2e>url()</code> references to gallery images (blocked by sanitizer)</td></tr></tbody></table><p class="small text-muted mt-2 mb-0" data-v-1f12fa2e> The template CSS sanitizer strips non-<code data-v-1f12fa2e>data:</code> URLs in stylesheets for security. Use <code data-v-1f12fa2e>&lt;img&gt;</code> tags instead of CSS background images. </p></div></div><div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-info-circle me-2 text-info" data-v-1f12fa2e></i>Tips</div><div class="card-body" data-v-1f12fa2e><ul class="small mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Each project can hold up to <strong data-v-1f12fa2e>20 images</strong>, each up to <strong data-v-1f12fa2e>2 MB</strong>.</li><li class="mb-2" data-v-1f12fa2e>Images are served with a 24-hour browser cache header, so they load quickly in previews.</li><li class="mb-2" data-v-1f12fa2e>Use the <strong data-v-1f12fa2e>Rename</strong> button to give images descriptive names for easy identification.</li><li data-v-1f12fa2e>For logos and icons, <strong data-v-1f12fa2e>SVG</strong> or <strong data-v-1f12fa2e>WebP</strong> formats give the best quality-to-size ratio.</li></ul></div></div>',2))])):n("",!0),i.value==="markdown"?(o(),r("div",dt,[t[109]||(t[109]=c('<h4 class="section-title" data-v-1f12fa2e><i class="bi bi-markdown me-2 text-primary" data-v-1f12fa2e></i>Markdown Templates</h4><p class="text-muted" data-v-1f12fa2e>Markdown templates let you write reports in GitHub Flavoured Markdown (GFM) combined with Mustache syntax. The editor switches to a Markdown language mode, and both the live preview and server-side renders parse the Markdown before display.</p><div class="row g-4 mb-4" data-v-1f12fa2e><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-check-circle me-2 text-success" data-v-1f12fa2e></i>When to use Markdown</div><div class="card-body" data-v-1f12fa2e><ul class="small mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Text-heavy reports — summaries, memos, executive briefings</li><li class="mb-2" data-v-1f12fa2e>Simple tables from query data without custom styling</li><li class="mb-2" data-v-1f12fa2e>Reports where you want to write content quickly without HTML boilerplate</li><li data-v-1f12fa2e>Situations where the AI assistant&#39;s output is primarily prose</li></ul></div></div></div><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-x-circle me-2 text-danger" data-v-1f12fa2e></i>When to use HTML instead</div><div class="card-body" data-v-1f12fa2e><ul class="small mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Multi-column layouts with Bootstrap grid</li><li class="mb-2" data-v-1f12fa2e>Precise per-page styling with custom CSS</li><li class="mb-2" data-v-1f12fa2e>KPI tiles, charts, or complex badge styling</li><li data-v-1f12fa2e>Reports that require <code data-v-1f12fa2e>.report-page</code> divs with controlled page breaks</li></ul></div></div></div></div>',3)),a("div",lt,[t[103]||(t[103]=a("div",{class:"card-header"},[a("i",{class:"bi bi-braces me-2"}),e("Mustache works the same way")],-1)),a("div",it,[a("p",rt,[t[97]||(t[97]=e("All Mustache syntax — ",-1)),a("code",null,s(d.variable),1),t[98]||(t[98]=e(", ",-1)),a("code",null,s(d.section),1),t[99]||(t[99]=e(", ",-1)),a("code",null,s(d.inverted),1),t[100]||(t[100]=e(", dot notation — is evaluated first, then the result is parsed as Markdown. The ",-1)),a("code",null,s(d.rows_open),1),t[101]||(t[101]=e(" / ",-1)),a("code",null,s(d.rows_close),1),t[102]||(t[102]=e(" pattern still applies.",-1))]),a("pre",ot,s(l.markdown_basic),1)])]),a("div",nt,[t[108]||(t[108]=a("div",{class:"card-header"},[a("i",{class:"bi bi-table me-2"}),e("GFM tables with dynamic rows")],-1)),a("div",ct,[a("p",ft,[t[104]||(t[104]=e("Place the ",-1)),a("code",null,s(d.rows_open),1),t[105]||(t[105]=e(" loop inside the table body. Each iteration appends a row. Note: the closing ",-1)),a("code",null,s(d.rows_close),1),t[106]||(t[106]=e(" must sit on its own line.",-1))]),a("pre",vt,s(l.markdown_table),1),t[107]||(t[107]=a("div",{class:"alert alert-info mt-3 mb-0 py-2"},[a("i",{class:"bi bi-info-circle me-2"}),e(" Do not put blank lines between the pipe rows — GFM interprets a blank line as the end of the table. ")],-1))])]),t[110]||(t[110]=c('<div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-file-break me-2" data-v-1f12fa2e></i>Page breaks</div><div class="card-body" data-v-1f12fa2e><p class="small text-muted mb-2" data-v-1f12fa2e>Inline HTML is allowed inside Markdown templates. Use a div with <code data-v-1f12fa2e>page-break-after</code> to force a new page in PDF exports and print:</p><pre class="code-block" data-v-1f12fa2e>&lt;div style=&quot;page-break-after: always&quot;&gt;&lt;/div&gt;</pre></div></div><div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-list-check me-2" data-v-1f12fa2e></i>Supported Markdown features</div><div class="card-body p-0" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Syntax</th><th data-v-1f12fa2e>Output</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e># Heading</code> / <code data-v-1f12fa2e>## H2</code> / <code data-v-1f12fa2e>### H3</code></td><td data-v-1f12fa2e>Heading elements</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>**bold**</code> / <code data-v-1f12fa2e>*italic*</code></td><td data-v-1f12fa2e>Strong / emphasis</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>- item</code> / <code data-v-1f12fa2e>1. item</code></td><td data-v-1f12fa2e>Unordered / ordered lists</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>- [x] done</code> / <code data-v-1f12fa2e>- [ ] todo</code></td><td data-v-1f12fa2e>Task list checkboxes</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>&gt; blockquote</code></td><td data-v-1f12fa2e>Callout / pull-quote block</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>`code`</code> / <code data-v-1f12fa2e>```block```</code></td><td data-v-1f12fa2e>Inline / fenced code</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>| Col | Col |</code> + header separator</td><td data-v-1f12fa2e>GFM table</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>---</code></td><td data-v-1f12fa2e>Horizontal rule</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e>Inline HTML</td><td data-v-1f12fa2e>Passed through (page breaks, images, etc.)</td></tr></tbody></table></div></div>',2))])):n("",!0),i.value==="scheduling"?(o(),r("div",pt,[...t[111]||(t[111]=[c('<h4 class="section-title" data-v-1f12fa2e><i class="bi bi-clock-history me-2 text-primary" data-v-1f12fa2e></i>Scheduling</h4><p class="text-muted" data-v-1f12fa2e>Schedules automate report rendering on a recurring basis using standard cron expressions. The app&#39;s service principal executes the query and renders the template server-side — no user session is required.</p><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-lightning me-2 text-warning" data-v-1f12fa2e></i>Quick start</div><div class="card-body" data-v-1f12fa2e><ol class="mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Make sure the app&#39;s service principal has <code data-v-1f12fa2e>SELECT</code> privilege on every Unity Catalog table used by the report&#39;s data structure.</li><li class="mb-2" data-v-1f12fa2e>Open <strong data-v-1f12fa2e>Schedules</strong> from the sidebar (an active project must be selected).</li><li class="mb-2" data-v-1f12fa2e>Click <strong data-v-1f12fa2e>New Schedule</strong>, choose a data structure and template, set a frequency, and click <strong data-v-1f12fa2e>Create Schedule</strong>.</li><li class="mb-2" data-v-1f12fa2e>The schedule is registered immediately. Use the <i class="bi bi-play-fill" data-v-1f12fa2e></i> button to trigger a test run without waiting for the next cron tick.</li><li data-v-1f12fa2e>Switch to the <strong data-v-1f12fa2e>Execution History</strong> tab and click <i class="bi bi-list-check" data-v-1f12fa2e></i> on any schedule to review past runs and error messages.</li></ol></div></div><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-exclamation-triangle me-2 text-warning" data-v-1f12fa2e></i>Service principal requirement</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e> Scheduled executions run in the background without a user session. The app queries Databricks using the <strong data-v-1f12fa2e>service principal credentials</strong> configured in the environment (<code data-v-1f12fa2e>DATABRICKS_CLIENT_ID</code> / <code data-v-1f12fa2e>DATABRICKS_CLIENT_SECRET</code> or <code data-v-1f12fa2e>DATABRICKS_TOKEN</code>). </p><p class="small mb-0 text-danger fw-semibold" data-v-1f12fa2e> If the service principal does not have <code data-v-1f12fa2e>SELECT</code> on the relevant UC tables, every scheduled execution will fail with a permissions error. </p></div></div><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-calendar-week me-2" data-v-1f12fa2e></i>Cron expression format</div><div class="card-body" data-v-1f12fa2e><p class="small text-muted mb-3" data-v-1f12fa2e>Schedules use standard 5-field cron syntax: <code data-v-1f12fa2e>minute hour day month day_of_week</code>.</p><table class="table table-sm mb-3" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Expression</th><th data-v-1f12fa2e>Meaning</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>0 9 * * *</code></td><td data-v-1f12fa2e>Every day at 09:00</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>0 9 * * 1-5</code></td><td data-v-1f12fa2e>Weekdays (Mon–Fri) at 09:00</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>0 8 * * 1</code></td><td data-v-1f12fa2e>Every Monday at 08:00</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>0 6 1 * *</code></td><td data-v-1f12fa2e>1st of every month at 06:00</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>*/15 * * * *</code></td><td data-v-1f12fa2e>Every 15 minutes</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><code data-v-1f12fa2e>30 17 * * 5</code></td><td data-v-1f12fa2e>Every Friday at 17:30</td></tr></tbody></table><p class="small text-muted mb-0" data-v-1f12fa2e> The schedule builder&#39;s <strong data-v-1f12fa2e>Simple</strong> mode generates a cron expression for you. Switch to <strong data-v-1f12fa2e>Cron</strong> mode to enter one manually. </p></div></div><div class="card mb-4" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-list-check me-2" data-v-1f12fa2e></i>Execution statuses</div><div class="card-body p-0" data-v-1f12fa2e><table class="table table-sm mb-0" data-v-1f12fa2e><thead class="table-dark" data-v-1f12fa2e><tr data-v-1f12fa2e><th data-v-1f12fa2e>Status</th><th data-v-1f12fa2e>Meaning</th></tr></thead><tbody data-v-1f12fa2e><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge bg-primary" data-v-1f12fa2e>running</span></td><td data-v-1f12fa2e>The execution is in progress. The history panel auto-refreshes every 10 seconds while a run is active.</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge bg-success" data-v-1f12fa2e>success</span></td><td data-v-1f12fa2e>The report rendered without error.</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge bg-danger" data-v-1f12fa2e>failed</span></td><td data-v-1f12fa2e>The run failed — check the <strong data-v-1f12fa2e>Error</strong> column for details (missing UC privilege, bad Mustache syntax, warehouse timeout, etc.).</td></tr><tr data-v-1f12fa2e><td data-v-1f12fa2e><span class="badge bg-secondary" data-v-1f12fa2e>pending</span></td><td data-v-1f12fa2e>Queued but not yet started.</td></tr></tbody></table></div></div><div class="row g-4 mb-4" data-v-1f12fa2e><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-pencil me-2 text-primary" data-v-1f12fa2e></i>Editing a schedule</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>Click the <i class="bi bi-pencil" data-v-1f12fa2e></i> button to change a schedule&#39;s <strong data-v-1f12fa2e>name</strong>, <strong data-v-1f12fa2e>cron expression</strong>, or <strong data-v-1f12fa2e>active</strong> status.</p><p class="small mb-2" data-v-1f12fa2e>The linked structure and template cannot be changed after creation — delete and recreate the schedule if you need a different template.</p><p class="small mb-0 text-muted" data-v-1f12fa2e>Saving a cron change re-registers the APScheduler job immediately.</p></div></div></div><div class="col-md-6" data-v-1f12fa2e><div class="card h-100" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-toggle-on me-2 text-success" data-v-1f12fa2e></i>Active vs Inactive</div><div class="card-body" data-v-1f12fa2e><p class="small mb-2" data-v-1f12fa2e>Inactive schedules are not registered with the scheduler — they will not fire automatically.</p><p class="small mb-2" data-v-1f12fa2e>Toggling a schedule back to <strong data-v-1f12fa2e>Active</strong> immediately re-registers the cron job with no further action required.</p><p class="small mb-0 text-muted" data-v-1f12fa2e>The manual trigger button (<i class="bi bi-play-fill" data-v-1f12fa2e></i>) works regardless of the active flag.</p></div></div></div></div><div class="card" data-v-1f12fa2e><div class="card-header" data-v-1f12fa2e><i class="bi bi-info-circle me-2 text-info" data-v-1f12fa2e></i>Tips &amp; limitations</div><div class="card-body" data-v-1f12fa2e><ul class="small mb-0" data-v-1f12fa2e><li class="mb-2" data-v-1f12fa2e>Schedules are scoped to a project — select the project in the sidebar before navigating to the Schedules page.</li><li class="mb-2" data-v-1f12fa2e>The scheduler runs in the same process as the FastAPI back-end. If the app restarts, all active schedules are automatically re-registered from the database on startup.</li><li class="mb-2" data-v-1f12fa2e>Execution history is paginated to the last 50 runs by default. Use the offset/limit query parameters on the API if you need older entries.</li><li class="mb-2" data-v-1f12fa2e>Only the project owner and shared members can create or modify schedules. The <code data-v-1f12fa2e>check_schedule_project_access</code> guard applies the same access + lock rules as structures and templates.</li><li data-v-1f12fa2e>Scheduled renders use a <strong data-v-1f12fa2e>10,000 row limit</strong> on the SQL query — the same as a full PDF export.</li></ul></div></div>',8)])])):n("",!0)])])]))}}),yt=h(mt,[["__scopeId","data-v-1f12fa2e"]]);export{yt as default};
